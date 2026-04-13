#!/usr/bin/env python3
"""
context-db-sub-agent.py — spawns claude -p for isolated context-db lookups.

Only called when mode=sub-agent. The main agent calls this based on
instructions from context-db-main-agent.py.

Spawns claude -p with system prompt + user message from prompts/ templates.
Parses stream-json output. Returns [response] + [response-instructions].

Sub-commands:
  prompt        Consult context-db for knowledge/standards
  pre-review    Check plan against standards before implementing
  review        Review changes against conventions
  update        File learnings into context-db

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


# Tools granted to each command's sub-agent
COMMAND_TOOLS = {
    "prompt": "Bash,Read",
    "pre-review": "Bash,Read",
    "review": "Bash,Read",
    "update": "Bash,Read,Write,Edit",
}


# ── Path discovery ──────────────────────────────────────────────────────────


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


# ── Template loading ────────────────────────────────────────────────────────


def load_template(name):
    """Load a prompt template from the prompts/ directory."""
    prompts_dir = Path(__file__).resolve().parent / "prompts"
    path = prompts_dir / f"{name}.md"
    if not path.exists():
        sys.exit(f"Error: template not found: {path}")
    return path.read_text()


def fill_template(template, **kwargs):
    """Fill {variables} in a template."""
    for key, value in kwargs.items():
        template = template.replace(f"{{{key}}}", str(value))
    return template


# ── Sub-agent execution ─────────────────────────────────────────────────────


def spawn_claude(system_prompt, user_msg, model, tools, cwd, debug=False):
    """Run claude -p subprocess and return (response_text, cost_usd, elapsed)."""
    cmd = [
        "claude",
        "-p",
        "--model",
        model,
        "--tools",
        tools,
        "--output-format",
        "stream-json",
        "--verbose",
        "--no-session-persistence",
        "--permission-mode",
        "bypassPermissions",
        "--system-prompt",
        system_prompt,
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
                        elif tool == "Write":
                            print(f"  writing: {inp.get('file_path', '')}",
                                  flush=True)
                        elif tool == "Edit":
                            print(f"  editing: {inp.get('file_path', '')}",
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


# ── Main ────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="context-db sub-agent")
    parser.add_argument(
        "command",
        choices=["prompt", "pre-review", "review", "update"],
    )
    parser.add_argument("prompt", nargs="?", default="")
    parser.add_argument("--model", default="haiku")
    parser.add_argument("--review-type", default="context-db",
                        choices=["context-db", "full"])
    parser.add_argument("--debug", action="store_true")

    args = parser.parse_args()

    if not args.prompt:
        parser.error(f"{args.command} requires a prompt")

    toc = find_toc_script()
    context_db_rel = find_context_db()
    cwd = os.getcwd()
    debug = args.debug

    # Load system prompt template
    if args.command == "review" and args.review_type == "full":
        system_template = load_template("system-review-full")
    else:
        system_template = load_template(f"system-{args.command}")

    system_prompt = fill_template(system_template, toc=toc,
                                  context_db_rel=context_db_rel)

    # Load user message template
    user_template = load_template(f"user-{args.command}")
    user_msg = fill_template(user_template, prompt=args.prompt)

    # Load response instructions
    response_instructions = load_template(f"response-{args.command}")

    if debug:
        print(f"cwd: {cwd}")
        print(f"context-db: {context_db_rel}/")
        print(f"model: {args.model}")
        print(f"\n[system prompt]\n{system_prompt}\n[end]")
        print(f"\n[user message]\n{user_msg}\n[end]\n")

    text, cost_usd, elapsed = spawn_claude(
        system_prompt, user_msg, args.model,
        COMMAND_TOOLS[args.command], cwd, debug,
    )

    if text is None:
        sys.exit("Error: sub-agent timed out")

    print(f"\n[response]")
    print(text.strip())
    print(f"[end response]")

    print(f"\n[response-instructions]")
    print(response_instructions.strip())
    print(f"[end response-instructions]")

    if debug:
        print(f"\n[metadata]")
        print(f"model: {args.model} | cost: ${cost_usd:.4f} | time: {elapsed:.1f}s")


if __name__ == "__main__":
    main()
