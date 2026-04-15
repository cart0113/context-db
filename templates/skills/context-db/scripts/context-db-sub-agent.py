#!/usr/bin/env python3
"""
context-db-sub-agent.py — spawns claude -p for isolated context-db lookups.

Composes system prompt from main-agent templates (shared) + sub-agent templates
(additional constraints for cheap models). Wraps the response in tagged blocks
for the main agent.

Sub-commands:
  prompt        Consult context-db for knowledge/standards
  pre-review    Check plan against standards before implementing
  review        Review changes against conventions

Usage:
  context-db-sub-agent.py prompt "user instruction"
  context-db-sub-agent.py prompt "user instruction" --model sonnet
  context-db-sub-agent.py review "summary" --review-type full --debug

Dependencies: python3 (stdlib only), claude CLI
"""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path


# ── Template composition per command ──────────────────────────────────────
#
# System prompt = main-agent templates + sub-agent templates.
# Each entry is (directory, template_name).
#
# Main-agent templates provide navigation mechanics and command instructions.
# Sub-agent templates add hard constraints for cheap models and output format.

SYSTEM_TEMPLATES = {
    "prompt": [
        ("main-agent", "read-mechanics"),
        ("sub-agent", "role-prompt"),
        ("sub-agent", "output-format"),
    ],
    "pre-review": [
        ("sub-agent", "role"),
        ("main-agent", "read-mechanics"),
        ("main-agent", "pre-review"),
        ("sub-agent", "navigation-constraints"),
        ("sub-agent", "output-format"),
    ],
    "review": [
        ("sub-agent", "role"),
        ("main-agent", "read-mechanics"),
        ("main-agent", "review"),
        ("sub-agent", "navigation-constraints"),
        ("sub-agent", "output-format-review"),
    ],
    "review-full": [
        ("sub-agent", "role"),
        ("main-agent", "read-mechanics"),
        ("main-agent", "review"),
        ("sub-agent", "navigation-constraints"),
        ("sub-agent", "output-format-review-full"),
    ],
}

# Blocks prepended to the sub-agent's response before [context-db-findings].
# These are main-agent templates the calling agent needs as framing.
RESPONSE_PREFIX = {
    "prompt": [("main-agent", "context-usage")],
    "pre-review": [("main-agent", "context-usage")],
    "review": [],
    "review-full": [],
}

# Tools granted to each command's sub-agent.
COMMAND_TOOLS = {
    "prompt": "Bash,Read",
    "pre-review": "Bash,Read",
    "review": "Bash,Read",
}


# ── Path discovery ────────────────────────────────────────────────────────
# All paths relative to cwd — no symlink resolution, no absolute paths.


def find_toc_script():
    """Find context-db-generate-toc.py. Returns path relative to cwd."""
    rel = ".claude/skills/context-db/scripts/context-db-generate-toc.py"
    if os.path.exists(rel):
        return rel
    parent_rel = os.path.join("..", rel)
    if os.path.exists(parent_rel):
        return parent_rel
    candidate = Path(__file__).resolve().parent / "context-db-generate-toc.py"
    if candidate.exists():
        return str(candidate)
    return rel


def find_context_db():
    """Find context-db/ relative to cwd."""
    if os.path.isdir("context-db"):
        return "context-db"
    return "."


# ── Template loading ──────────────────────────────────────────────────────


def load_template(directory, name):
    """Load a prompt template from prompts/<directory>/<name>.md."""
    prompts_dir = Path(__file__).resolve().parent / "prompts" / directory
    path = prompts_dir / f"{name}.md"
    if not path.exists():
        sys.exit(f"Error: template not found: {path}")
    return path.read_text()


def fill_template(template, **kwargs):
    """Fill {variables} in a template."""
    for key, value in kwargs.items():
        template = template.replace(f"{{{key}}}", str(value))
    return template


def compose_templates(template_list, **kwargs):
    """Load and fill a list of (directory, name) templates, join with newlines."""
    parts = []
    for directory, name in template_list:
        template = load_template(directory, name)
        parts.append(fill_template(template, **kwargs))
    return "\n".join(parts)


def template_key(command, review_type):
    """Map command + review_type to a SYSTEM_TEMPLATES key."""
    if command == "review" and review_type == "full":
        return "review-full"
    return command


# ── Sub-agent execution ──────────────────────────────────────────────────


def spawn_claude(system_prompt, user_msg, model, tools, cwd, debug=False):
    """Run claude -p subprocess and return (response_text, cost_usd, elapsed).

    Uses stream-json output format so we can show debug progress (which files
    the sub-agent reads) without waiting for the full response.
    """
    cmd = [
        "claude",
        "-p",
        "--model", model,
        "--tools", tools,
        "--output-format", "stream-json",
        "--verbose",
        "--no-session-persistence",
        "--permission-mode", "bypassPermissions",
        "--system-prompt", system_prompt,
    ]

    env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
    env["CONTEXT_DB_SUBAGENT"] = "1"
    start = time.time()
    final_text = ""
    cost_usd = 0.0

    try:
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
            cwd=cwd,
        )
        proc.stdin.write(user_msg)
        proc.stdin.close()

        for line in proc.stdout:
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue

            etype = event.get("type", "")

            if etype == "assistant" and debug:
                for block in event.get("message", {}).get("content", []):
                    if block.get("type") == "tool_use":
                        tool = block["name"]
                        inp = block.get("input", {})
                        if tool == "Read":
                            print(f"  reading: {inp.get('file_path', '')}",
                                  flush=True)
                        elif tool == "Bash":
                            print(f"  running: {inp.get('command', '')}",
                                  flush=True)

            elif etype == "result":
                final_text = event.get("result", "")
                cost_usd = event.get("total_cost_usd", 0.0)

        proc.wait(timeout=3600)
    except subprocess.TimeoutExpired:
        proc.kill()
        return None, 0.0, time.time() - start
    except FileNotFoundError:
        sys.exit("Error: 'claude' CLI not found")

    if proc.returncode != 0:
        stderr = proc.stderr.read()
        sys.exit(f"Error: {stderr}")

    return final_text, cost_usd, time.time() - start


# ── Main ─────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="context-db sub-agent")
    parser.add_argument(
        "command",
        choices=["prompt", "pre-review", "review"],
    )
    parser.add_argument("prompt", nargs="?", default="")
    parser.add_argument("--model", default="haiku")
    parser.add_argument("--review-type", default="context-db",
                        choices=["context-db", "full"])
    parser.add_argument("--rerun-init", action="store_true",
                        help="Reload init templates after response")
    parser.add_argument("--debug", action="store_true")

    args = parser.parse_args()

    if not args.prompt:
        parser.error(f"{args.command} requires a prompt")

    toc = find_toc_script()
    context_db_rel = find_context_db()
    cwd = os.getcwd()
    key = template_key(args.command, args.review_type)

    # Compose system prompt: templates + user prompt injected as data
    # The prompt goes into the system prompt as [main-user-prompt] so the
    # sub-agent sees it as content to look up, not a task to perform.
    templates_text = compose_templates(
        SYSTEM_TEMPLATES[key], toc=toc, context_db_rel=context_db_rel,
    )
    # Insert [main-user-prompt] after the first template (read-mechanics)
    # so the model sees: what context-db is → what to look up → its role
    parts = templates_text.split("\n[sub-agent-role]", 1)
    prompt_block = (
        f"\n[main-user-prompt]\n\n{args.prompt}\n\n[end main-user-prompt]\n"
    )
    system_prompt = parts[0] + prompt_block + "\n[sub-agent-role]" + parts[1]

    # User message — simple trigger, the real prompt is in the system prompt
    user_msg = "Find relevant context from context-db for the prompt above."

    if args.debug:
        print(f"cwd: {cwd}")
        print(f"context-db: {context_db_rel}/")
        print(f"model: {args.model}")
        print(f"\n[system-prompt]\n{system_prompt}\n[end system-prompt]")
        print(f"\n[user-message]\n{user_msg}\n[end user-message]\n")

    text, cost_usd, elapsed = spawn_claude(
        system_prompt, user_msg, args.model,
        COMMAND_TOOLS[args.command], cwd, args.debug,
    )

    if text is None:
        sys.exit("Error: sub-agent timed out")

    # Response: prefix blocks (e.g. context-usage) + findings
    prefix = compose_templates(
        RESPONSE_PREFIX[key], toc=toc, context_db_rel=context_db_rel,
    )
    if prefix.strip():
        print(prefix)

    print(f"\n[context-db-findings]\n")
    print(text.strip())
    print(f"\n[end context-db-findings]")

    # Optionally reload init templates after response
    if args.rerun_init:
        config_path = os.path.join(cwd, "context-db.json")
        init_templates = ["read-mechanics", "persist-to-context-db"]
        if os.path.exists(config_path):
            with open(config_path) as f:
                config = json.load(f)
            init_templates = config.get("init", init_templates)
        for name in init_templates:
            template = load_template("main-agent", name)
            print(fill_template(template, toc=toc,
                                context_db_rel=context_db_rel))

    if args.debug:
        print(f"\n[sub-agent-metadata]")
        print(f"model: {args.model} | cost: ${cost_usd:.4f} "
              f"| time: {elapsed:.1f}s")
        print(f"[end sub-agent-metadata]")


if __name__ == "__main__":
    main()
