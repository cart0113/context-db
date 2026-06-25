#!/usr/bin/env python3
"""
context-db-main-agent.py — dispatcher for the /context-db skill.

Prints tagged instruction blocks the calling agent follows directly. The agent
navigates context-db itself with its own Read/Bash tools — there is no
sub-process, no model selection, and no configuration file.

Commands:
  prompt    Consult the knowledge base for a piece of work.
  update    File learnings into context-db.
  maintain  Audit and maintain context-db.
  read      Read everything under a context-db folder, exhaustively.
  help      Show usage (alias for --help).

Optional special files at the root of context-db/ are inlined automatically
when their command runs, if they exist:

  context-db/ON_PROMPT.md     → inlined on `prompt`
  context-db/ON_UPDATE.md     → inlined on `update`
  context-db/ON_MAINTAIN.md   → inlined on `maintain`

Dependencies: python3 (stdlib only)
"""

import argparse
import subprocess
import sys
from pathlib import Path


# ── Path discovery ───────────────────────────────────────────────────────────
# Paths are returned relative to cwd so the agent's Bash/Read calls work without
# absolute-path issues. Search order: standard .claude/ location → parent dir →
# __file__ fallback.


def _find_script(filename):
    """Find a sibling script. Returns a path relative to cwd when possible."""
    rel = f".claude/skills/context-db/scripts/{filename}"
    if Path(rel).exists():
        return rel
    parent_rel = Path("..") / rel
    if parent_rel.exists():
        return str(parent_rel)
    candidate = Path(__file__).resolve().parent / filename
    if candidate.exists():
        return str(candidate)
    return rel


def find_toc_script():
    return _find_script("context-db-generate-toc.py")


def find_resolve_script():
    return _find_script("context-db-resolve-path.py")


def find_context_db():
    """Find context-db/ relative to cwd."""
    if Path("context-db").is_dir():
        return "context-db"
    return "."


def find_project_folders(context_db_rel):
    """Return sorted names of top-level `*-project/` folders inside context-db/.

    Convention: a single `context-db/<name>-project/` folder holds knowledge
    specific to this repo. Other top-level folders are external — global
    standards, shared conventions, or folders symlinked in from other repos.
    Returns `[]` if context-db is missing or no project folder exists.
    """
    if context_db_rel == "." or not Path(context_db_rel).is_dir():
        return []
    base = Path(context_db_rel)
    return sorted(p.name for p in base.glob("*-project") if p.is_dir())


# ── Special files ─────────────────────────────────────────────────────────────
# Fixed-name, optional files at the root of context-db/. Inlined raw (frontmatter
# stripped) when the matching command runs. No configuration — presence is the
# only switch.

SPECIAL_FILE = {
    "prompt": "ON_PROMPT.md",
    "update": "ON_UPDATE.md",
    "maintain": "ON_MAINTAIN.md",
}


def special_file_path(command, context_db_rel):
    """Path to the special file for `command`, or None if not applicable."""
    name = SPECIAL_FILE.get(command)
    if not name:
        return None
    return Path(context_db_rel) / name


def emit_special_file(command, context_db_rel):
    """Inline context-db/ON_<COMMAND>.md raw, if it exists."""
    path = special_file_path(command, context_db_rel)
    if path and path.is_file():
        print(f"\n{strip_frontmatter(path.read_text()).rstrip()}")


# ── Git diff collection ───────────────────────────────────────────────────────
# Used by --use-git-diff on `prompt` to surface context-db files touched
# recently (likely relevant to where a prior session left off).

DIFF_LINE_CAP = 500


def collect_recent_changes(context_db_rel, n):
    """Collect recent git changes in context-db/. Returns formatted block, or None.

    n=0: uncommitted changes only.
    n>0: uncommitted + last n commits touching context-db/.

    If the combined diff exceeds DIFF_LINE_CAP, falls back to a --stat summary.
    """
    if context_db_rel == ".":
        return None

    def run(args):
        try:
            r = subprocess.run(args, capture_output=True, text=True, timeout=10)
            return r.stdout if r.returncode == 0 else ""
        except (subprocess.SubprocessError, FileNotFoundError):
            return ""

    sections = []  # list of (header, stat_text, full_diff_text)

    uncommitted_full = run(["git", "diff", "HEAD", "--", context_db_rel])
    if uncommitted_full.strip():
        uncommitted_stat = run(
            ["git", "diff", "HEAD", "--stat", "--", context_db_rel]
        )
        sections.append(
            ("## Uncommitted Changes", uncommitted_stat, uncommitted_full)
        )

    if n > 0:
        commits_full = run(
            ["git", "log", "-n", str(n), "-p", "--", context_db_rel]
        )
        if commits_full.strip():
            commits_stat = run([
                "git", "log", "-n", str(n), "--stat",
                "--format=%h %s", "--", context_db_rel,
            ])
            header = f"## Last {n} Commit{'s' if n != 1 else ''}"
            sections.append((header, commits_stat, commits_full))

    if not sections:
        return None

    total_lines = sum(len(full.splitlines()) for _, _, full in sections)
    use_stat = total_lines > DIFF_LINE_CAP

    out = []
    if use_stat:
        out.append(
            f"(Diff exceeded {DIFF_LINE_CAP} lines — showing file stats only. "
            f"Use `git diff HEAD -- {context_db_rel}/` or "
            f"`git log -p -n {n} -- {context_db_rel}/` for full content.)\n"
        )
    for header, stat, full in sections:
        out.append(header)
        out.append("")
        out.append((stat if use_stat else full).strip())
        out.append("")

    return "\n".join(out).strip()


# ── Frontmatter ───────────────────────────────────────────────────────────────


def strip_frontmatter(text):
    """Strip a leading YAML frontmatter block (delimited by ---) from text.

    If no frontmatter is present or the block is malformed, returns the original
    text unchanged.
    """
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].rstrip() != "---":
        return text
    for i in range(1, len(lines)):
        if lines[i].rstrip() == "---":
            return "".join(lines[i + 1:]).lstrip("\n")
    return text


# ── Template loading ──────────────────────────────────────────────────────────
# Prompt templates live in prompts/main-agent/*.md. Each carries a single H1
# header as its section delimiter. Variables use {name} syntax.


def load_template(name):
    """Load a prompt template from prompts/main-agent/<name>.md."""
    path = Path(__file__).resolve().parent / "prompts" / "main-agent" / f"{name}.md"
    if not path.exists():
        sys.exit(f"Error: template not found: {path}")
    return path.read_text()


def fill_template(template, **kwargs):
    """Fill {variables} in a template. Unknown variables are left as-is."""
    for key, value in kwargs.items():
        template = template.replace(f"{{{key}}}", str(value))
    return template


def print_template(name, **kwargs):
    """Load a template, fill variables, and print. The H1 header lives in the file."""
    print()
    print(fill_template(load_template(name), **kwargs))


def print_section(tag, content):
    """Print a dynamically H1-delimited section for content with no template file."""
    title = tag.replace("-", " ").title()
    print(f"\n# {title}\n")
    print(content.strip())


# ── Project-folder reinforcement ──────────────────────────────────────────────
# For write commands, name the project folder so the agent writes there (not
# into parallel folders, which are external/shared).


def emit_project_folder_reinforcement(context_db_rel):
    folders = find_project_folders(context_db_rel)
    if not folders:
        return
    if len(folders) == 1:
        body = (
            f"This repo's project folder is `{context_db_rel}/{folders[0]}/`. "
            f"That is where knowledge specific to this project lives. Other "
            f"top-level folders under `{context_db_rel}/` are external — "
            f"global standards, shared conventions, or folders symlinked in "
            f"from other repos.\n\n"
            f"When writing or maintaining context-db, default to writing "
            f"inside the project folder. Only edit a parallel folder when the "
            f"content is genuinely not project-specific."
        )
    else:
        items = "\n".join(f"- `{context_db_rel}/{f}/`" for f in folders)
        body = (
            f"Multiple `*-project/` folders exist at the top level of "
            f"`{context_db_rel}/`:\n\n{items}\n\n"
            f"Convention is one project folder per repo. Mention this to the "
            f"user — they may want to consolidate. In the meantime, write to "
            f"whichever is the active project folder for the current task."
        )
    print_section("project-folder", body)


def emit_special_file_notice(command, context_db_rel):
    """Warn write commands (update, maintain) before they touch a special file.

    The special files are inlined into the agent's context on every matching
    command, so every line in them costs tokens repeatedly. No-op if none exist.
    """
    existing = [
        (cmd, special_file_path(cmd, context_db_rel))
        for cmd in SPECIAL_FILE
    ]
    existing = [(cmd, p) for cmd, p in existing if p and p.is_file()]
    if not existing:
        return
    lines = ["\n# Always-Read Files", ""]
    lines.append(
        "These files are inlined into the agent's context automatically on "
        "every matching /context-db command, so every line costs tokens "
        "repeatedly. Use strong judgement before writing to them — most "
        "learnings belong in a regular context-db file, not here. When in "
        "doubt, ask the user first."
    )
    lines.append("")
    for cmd, path in existing:
        lines.append(f"- `{path}` — inlined on every /context-db {cmd}")
    print("\n".join(lines))


# ── Command handlers ──────────────────────────────────────────────────────────


def cmd_prompt(args):
    toc = find_toc_script()
    resolve = find_resolve_script()
    context_db_rel = find_context_db()

    if not args.instruction:
        print("No instruction provided. Ask the user what they want to prompt.")
        return

    print_template("read-mechanics", toc=toc, resolve=resolve,
                   context_db_rel=context_db_rel)
    print_template("context-usage")
    if args.use_git_diff is not None:
        block = collect_recent_changes(context_db_rel, args.use_git_diff)
        if block:
            print_template("recent-changes", recent_changes_block=block)
    print_template("prompt")
    emit_special_file("prompt", context_db_rel)
    print_section("prompt-user-instructions", args.instruction)


def cmd_update(args):
    toc = find_toc_script()
    resolve = find_resolve_script()
    context_db_rel = find_context_db()
    commit = args.commit or args.push

    if commit:
        print_template("read-mechanics", toc=toc, resolve=resolve,
                       context_db_rel=context_db_rel)
    print_template("write-mechanics", toc=toc, context_db_rel=context_db_rel)
    emit_project_folder_reinforcement(context_db_rel)
    print_template("persist-to-context-db")
    print_template("update-general", context_db_rel=context_db_rel)
    emit_special_file_notice("update", context_db_rel)
    emit_special_file("update", context_db_rel)
    if args.instruction:
        print_section("update-user-instructions", args.instruction)
    if commit:
        print_template("update-commit")
    if args.push:
        print_template("update-push")


def cmd_maintain(args):
    toc = find_toc_script()
    resolve = find_resolve_script()
    context_db_rel = find_context_db()
    target_path = args.path if args.path else f"{context_db_rel}/"

    print_template("write-mechanics", toc=toc, context_db_rel=context_db_rel)
    emit_project_folder_reinforcement(context_db_rel)
    print_template("write-content-guide")
    print_template("maintain-instructions", toc=toc, resolve=resolve,
                   context_db_rel=context_db_rel, target_path=target_path)
    emit_special_file_notice("maintain", context_db_rel)
    emit_special_file("maintain", context_db_rel)


def cmd_read(args):
    toc = find_toc_script()
    context_db_rel = find_context_db()
    target_path = args.folder if args.folder else f"{context_db_rel}/"
    print_template("read", toc=toc, context_db_rel=context_db_rel,
                   target_path=target_path)


# ── CLI ───────────────────────────────────────────────────────────────────────


def build_parser():
    parser = argparse.ArgumentParser(
        prog="context-db",
        description="Project knowledge base",
    )
    subs = parser.add_subparsers(dest="command")

    p = subs.add_parser("prompt", help="Consult the knowledge base")
    p.add_argument("instruction", nargs="?", default="")
    p.add_argument(
        "--use-git-diff", nargs="?", const=3, default=None, type=int,
        metavar="N",
        help="Surface recently changed context-db files first. "
             "N=commits (default 3, 0=uncommitted only).",
    )

    up = subs.add_parser("update", help="File learnings into context-db")
    up.add_argument("instruction", nargs="?", default="")
    up.add_argument("--commit", action="store_true",
                    help="Commit affected files after updating context-db")
    up.add_argument("--push", action="store_true",
                    help="Push after committing (implies --commit)")

    mt = subs.add_parser("maintain", help="Audit and maintain context-db")
    mt.add_argument("path", nargs="?", default="")

    rd = subs.add_parser(
        "read", help="Read everything under a context-db folder, exhaustively")
    rd.add_argument("folder", nargs="?", default="")

    subs.add_parser("help", help="Show this help message")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if not args.command or args.command == "help":
        parser.print_help()
        return

    handlers = {
        "prompt": cmd_prompt,
        "update": cmd_update,
        "maintain": cmd_maintain,
        "read": cmd_read,
    }
    handlers[args.command](args)


if __name__ == "__main__":
    main()
