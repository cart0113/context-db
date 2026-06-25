#!/usr/bin/env python3
"""
Generate docs/src/reference/cli.md from the dispatcher's --help output and
the canonical prompt-template text.

For each subcommand, the page shows:
  1. The argparse --help block (CLI surface)
  2. The verbatim instruction template the agent reads
     (from .claude/skills/context-db/scripts/prompts/main-agent/<name>.md)

Run from anywhere:
    python3 bin/build-cli-reference.py

Re-run whenever the dispatcher, its argparse setup, or the prompt templates
change. The pre-commit hook does this automatically.

Dependencies: python3 (stdlib only).
"""

import re
import subprocess
import sys
from pathlib import Path
from textwrap import dedent

REPO_ROOT = Path(__file__).resolve().parent.parent
DISPATCHER = (
    REPO_ROOT
    / ".claude/skills/context-db/scripts/context-db-main-agent.py"
)
PROMPTS_DIR = (
    REPO_ROOT
    / "templates/skills/context-db/scripts/prompts/main-agent"
)
OUT_PATH = REPO_ROOT / "docs/src/reference/cli.md"


# Subcommands surfaced as `/context-db <name>` to users. The instruction
# template name (under prompts/main-agent/) is paired where one exists.
SUBCOMMANDS = [
    ("prompt", "prompt"),
    ("update", "update-general"),
    ("maintain", "maintain-instructions"),
    ("read", "read"),
]


def help_text(args):
    """Return the dispatcher's --help output for the given args list."""
    result = subprocess.run(
        ["python3", str(DISPATCHER), *args, "--help"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    if result.returncode != 0:
        sys.exit(f"--help failed for {args!r}: {result.stderr}")
    return result.stdout.rstrip()


def strip_frontmatter(text):
    """Strip a leading YAML frontmatter block if present."""
    if not text.startswith("---"):
        return text.lstrip("\n")
    m = re.match(r"---\n.*?\n---\n", text, re.DOTALL)
    if not m:
        return text
    return text[m.end():].lstrip("\n")


def render_template_block(template_name):
    """Return the prompt template body without YAML frontmatter."""
    path = PROMPTS_DIR / f"{template_name}.md"
    if not path.exists():
        return f"_(template `{template_name}.md` not found)_"
    return strip_frontmatter(path.read_text()).rstrip()


def render_subcommand(name, template_name):
    """Render one subcommand section."""
    lines = []
    lines.append(f"## `/context-db {name}` {{#{name}}}")
    lines.append("")
    lines.append("**CLI**")
    lines.append("")
    lines.append("```text")
    lines.append(help_text([name]))
    lines.append("```")
    if template_name:
        lines.append("")
        lines.append("**Canonical instruction text** — what the dispatcher")
        lines.append("emits to the agent when this subcommand runs:")
        lines.append("")
        lines.append("```markdown")
        lines.append(render_template_block(template_name))
        lines.append("```")
        lines.append("")
        lines.append(
            f"_Source: `templates/skills/context-db/scripts/prompts/"
            f"main-agent/{template_name}.md`_"
        )
    lines.append("")
    return "\n".join(lines)


def main():
    if not DISPATCHER.exists():
        sys.exit(f"missing dispatcher: {DISPATCHER}")

    sections = [
        f"## Top-level\n\n```text\n{help_text([])}\n```\n",
    ]
    for name, template_name in SUBCOMMANDS:
        sections.append(render_subcommand(name, template_name))

    header = dedent(
        """\
        # CLI reference

        > [!note] Auto-generated. Do not edit by hand.
        >
        > This page is regenerated from the dispatcher's `--help` output and
        > the prompt templates under
        > `templates/skills/context-db/scripts/prompts/main-agent/` by
        > `bin/build-cli-reference.py`. The pre-commit hook re-runs the
        > script whenever the dispatcher or any prompt template changes.

        For each subcommand, this page shows the literal `--help` output and
        the verbatim instruction text the dispatcher emits to the agent at
        run time. For the higher-level guide, see
        [Commands](../guide/commands.md).

        """
    )

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(header + "\n".join(sections) + "\n")
    print(f"wrote {OUT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
