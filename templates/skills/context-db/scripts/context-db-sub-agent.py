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


# Tools granted to each command's sub-agent.
# Read-only commands get Bash+Read (run TOC script, read files).
# update also gets Write+Edit since it modifies context-db files.
COMMAND_TOOLS = {
    "prompt": "Bash,Read",
    "pre-review": "Bash,Read",
    "review": "Bash,Read",
    "update": "Bash,Read,Write,Edit",
}


# ── Path discovery ──────────────────────────────────────────────────────────
# Same search logic as main-agent — relative paths, no symlink resolution.


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
# Sub-agent templates are in prompts/ (not prompts/main-agent/).
# Three template types per command:
#   system-<cmd>.md  — system prompt for the sub-agent
#   user-<cmd>.md    — user message with {prompt} placeholder
#   response-<cmd>.md — instructions for the main agent on how to use the output


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
    """Run claude -p subprocess and return (response_text, cost_usd, elapsed).

    Uses stream-json output format so we can show debug progress (which files
    the sub-agent reads) without waiting for the full response. The final
    "result" event contains the sub-agent's answer text and cost.
    """
    cmd = [
        "claude",
        "-p",                        # pipe mode: stdin=user msg, stdout=output
        "--model", model,
        "--tools", tools,
        "--output-format", "stream-json",  # one JSON event per line
        "--verbose",
        "--no-session-persistence",        # ephemeral — no session state saved
        "--permission-mode", "bypassPermissions",  # sub-agent runs unattended
        "--system-prompt", system_prompt,
    ]

    # Strip ANTHROPIC_API_KEY so claude CLI uses its own auth.
    # Set CONTEXT_DB_SUBAGENT=1 so hooks/scripts can detect sub-agent context.
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

        # Stream JSON events line-by-line as the sub-agent works
        for line in proc.stdout:
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue

            etype = event.get("type", "")

            # In debug mode, print each tool call so the user sees progress
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

            # Final event — contains the sub-agent's text response and cost
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
# Assembles system prompt + user message from templates, spawns claude -p,
# then wraps the sub-agent's response in [response] tags so the main agent
# can parse and act on it.


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

    # Assemble the two prompt halves from templates:
    #   system prompt — role + read-mechanics + TOC instructions
    #   user message  — the user's actual request
    if args.command == "review" and args.review_type == "full":
        system_template = load_template("system-review-full")
    else:
        system_template = load_template(f"system-{args.command}")

    system_prompt = fill_template(system_template, toc=toc,
                                  context_db_rel=context_db_rel)

    user_template = load_template(f"user-{args.command}")
    user_msg = fill_template(user_template, prompt=args.prompt)

    # response-<cmd>.md tells the *main* agent how to use the sub-agent's output
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

    # Output format: tagged sections the main agent parses
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
