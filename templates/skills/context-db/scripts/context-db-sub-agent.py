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
        ("sub-agent", "prompt-sub-agent-role"),
        ("sub-agent", "output-format"),
    ],
    "pre-review": [
        ("main-agent", "read-mechanics"),
        ("sub-agent", "pre-review-instructions"),
    ],
    "review": [
        ("main-agent", "read-mechanics"),
        ("sub-agent", "review-instructions"),
    ],
    "context-db-only-review": [
        ("main-agent", "read-mechanics"),
        ("sub-agent", "review-instructions-context-db-only"),
    ],
}

# Blocks prepended to the sub-agent's response before [context-db-findings].
RESPONSE_PREFIX = {
    "prompt": [("main-agent", "context-usage")],
    "pre-review": [],
    "review": [],
    "context-db-only-review": [],
}

# Blocks appended after [context-db-findings] — tells the main agent how to
# interpret the sub-agent's response.
RESPONSE_SUFFIX = {
    "prompt": [],
    "pre-review": [("sub-agent", "interpreting-pre-review-response")],
    "review": [("sub-agent", "interpreting-review-response")],
    "context-db-only-review": [("sub-agent", "interpreting-review-response")],
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


def template_key(command, context_db_only_review=False):
    """Map command + flags to a SYSTEM_TEMPLATES key."""
    if command == "review" and context_db_only_review:
        return "context-db-only-review"
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
    parser.add_argument("--context-db-only-review", action="store_true",
                        help="Review only flags convention issues from context-db")
    parser.add_argument("--rerun-init", action="store_true",
                        help="Reload init templates after response")
    parser.add_argument("--debug", action="store_true")

    args = parser.parse_args()

    if not args.prompt and args.command not in ("review",):
        parser.error(f"{args.command} requires a prompt")

    toc = find_toc_script()
    context_db_rel = find_context_db()
    cwd = os.getcwd()
    key = template_key(args.command, getattr(args, "context_db_only_review", False))

    # Conditional template variables based on whether a prompt exists
    user_guidance_note = ""
    if args.prompt:
        user_guidance_note = (
            "Take the user's instructions in [user-guidance] into account "
            "when conducting your review.\n\n"
        )

    # Compose system prompt from templates
    templates_text = compose_templates(
        SYSTEM_TEMPLATES[key], toc=toc, context_db_rel=context_db_rel,
        user_guidance_note=user_guidance_note,
    )

    # Inject [user-guidance] right after [end read-mechanics] when prompt exists
    if args.prompt:
        marker = "[end read-mechanics]"
        parts = templates_text.split(marker, 1)
        prompt_block = (
            f"\n\n[user-guidance]\n\n{args.prompt}\n\n"
            f"[end user-guidance]"
        )
        system_prompt = parts[0] + marker + prompt_block + parts[1]
    else:
        system_prompt = templates_text

    # claude -p requires stdin; system prompt has everything
    user_msg = "."

    if args.debug:
        print(f"cwd: {cwd}")
        print(f"context-db: {context_db_rel}/")
        print(f"model: {args.model}")
        print(f"\n[sub-agent-system-prompt]\n{system_prompt}\n"
              f"[end sub-agent-system-prompt]\n")

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

    # Suffix blocks — tells the main agent how to interpret the response
    suffix = compose_templates(
        RESPONSE_SUFFIX[key], toc=toc, context_db_rel=context_db_rel,
    )
    if suffix.strip():
        print(suffix)

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
