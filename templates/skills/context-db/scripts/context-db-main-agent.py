#!/usr/bin/env python3
"""
context-db-main-agent.py — dispatcher for /context-db skill.

Always called by the main agent via SKILL.md. Reads config, determines mode,
and either:
  - Prints instructions for the main agent to follow directly (main-agent mode)
  - Prints instructions telling the main agent to call context-db-sub-agent.py
    (sub-agent mode)
  - Prints instructions to ask the user which mode (ask mode)

Every response includes a [reminder] block with available commands to handle
context rot.

Sub-commands:
  init          Startup instructions (called by rule, not in SKILL.md)
  prompt        Consult context-db for knowledge/standards
  pre-review    Check plan against standards before implementing
  review        Review changes against conventions
  update        File learnings into context-db
  maintain      7-phase audit + reindex

Usage:
  context-db-main-agent.py init
  context-db-main-agent.py prompt "user instruction"
  context-db-main-agent.py prompt "user instruction" --mode main-agent
  context-db-main-agent.py review "summary" --model opus --review-type full
  context-db-main-agent.py maintain context-db/subfolder/

Dependencies: python3 (stdlib only)
"""

import argparse
import json
import os
import sys
from pathlib import Path


# ── Config ──────────────────────────────────────────────────────────────────

COMMANDS = ["prompt", "pre-review", "review", "update", "maintain"]

DEFAULT_CONFIG = {
    "defaults": {
        "mode": "sub-agent",
        "model": "haiku",
    },
    "prompt": {},
    "pre-review": {},
    "review": {
        "model": "sonnet",
        "review-type": "context-db",
    },
    "update": {
        "mode": "main-agent",
        "model": "sonnet",
    },
    "maintain": {
        "mode": "main-agent",
    },
}


def load_config(config_path):
    """Load .contextdb.json, merge with defaults."""
    config = json.loads(json.dumps(DEFAULT_CONFIG))
    if os.path.exists(config_path):
        with open(config_path) as f:
            user = json.load(f)
        if "defaults" in user:
            config["defaults"].update(user["defaults"])
        for cmd in COMMANDS:
            if cmd in user:
                config[cmd].update(user[cmd])
    return config


def get_command_config(config, command):
    """Get effective config for a command (defaults merged with command-specific)."""
    effective = dict(config["defaults"])
    effective.update(config[command])
    return effective


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


def find_sub_agent_script():
    """Find context-db-sub-agent.py. Returns path relative to cwd."""
    rel = ".claude/skills/context-db/scripts/context-db-sub-agent.py"
    if os.path.exists(rel):
        return rel
    parent_rel = os.path.join("..", rel)
    if os.path.exists(parent_rel):
        return parent_rel
    candidate = Path(__file__).resolve().parent / "context-db-sub-agent.py"
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
    """Fill {variables} in a template. Unknown variables are left as-is."""
    for key, value in kwargs.items():
        template = template.replace(f"{{{key}}}", str(value))
    return template


# ── Output formatting ───────────────────────────────────────────────────────


def print_section(tag, content):
    """Print a tagged output section."""
    print(f"\n[{tag}]")
    print(content.strip())
    print(f"[end {tag}]")


def print_reminder():
    """Print the re-instruction reminder block."""
    reminder = load_template("reminder")
    print_section("reminder", reminder)


# ── Command handlers ────────────────────────────────────────────────────────


def cmd_init(args):
    """Print startup instructions for the main agent."""
    template = load_template("init-instructions")
    print(template.strip())


def cmd_main_agent(command, prompt, cmd_config, debug=False):
    """Print instructions for the main agent to navigate context-db directly."""
    toc = find_toc_script()
    context_db_rel = find_context_db()

    template_name = f"main-agent-{command}"
    template = load_template(template_name)
    output = fill_template(template, toc=toc, context_db_rel=context_db_rel,
                           prompt=prompt)

    if debug:
        print(f"mode: main-agent")
        print(f"context-db: {context_db_rel}/")
        print(f"toc: {toc}")

    print_section("instructions", output)
    print_reminder()


def cmd_sub_agent(command, prompt, cmd_config, debug=False):
    """Print instructions telling the main agent to call the sub-agent script."""
    sub_agent = find_sub_agent_script()
    model = cmd_config["model"]

    cmd_parts = [f"python3 {sub_agent} {command}"]
    cmd_parts.append(f'"{prompt}"')
    cmd_parts.append(f"--model {model}")
    if command == "review" and "review-type" in cmd_config:
        cmd_parts.append(f"--review-type {cmd_config['review-type']}")
    if debug:
        cmd_parts.append("--debug")

    run_cmd = " ".join(cmd_parts)

    response_template = load_template(f"response-{command}")

    instructions = (
        f"Run the following command and wait for the response:\n\n"
        f"  {run_cmd}\n\n"
        f"The command will output a [response] section with findings from the\n"
        f"project's context-db knowledge base.\n\n"
        f"When it returns:\n"
        f"{response_template.strip()}"
    )

    if debug:
        print(f"mode: sub-agent")
        print(f"model: {model}")

    print_section("instructions", instructions)
    print_reminder()


def cmd_ask_mode(command, prompt, cmd_config, debug=False):
    """Print instructions to ask the user which mode to use."""
    instructions = (
        f"Ask the user: Should I consult context-db as a **sub-agent** "
        f"(isolated lookup, faster) or **main-agent** (I navigate directly, "
        f"more thorough)?\n\n"
        f"Then re-run with their choice:\n"
        f"  /context-db {command} --mode <their-choice> {prompt}"
    )
    print_section("instructions", instructions)
    print_reminder()


def cmd_maintain(args, config):
    """Print the full 7-phase maintain instructions."""
    toc = find_toc_script()
    context_db_rel = find_context_db()
    target_path = args.prompt if args.prompt else f"{context_db_rel}/"

    template = load_template("maintain-instructions")
    output = fill_template(template, toc=toc, context_db_rel=context_db_rel,
                           target_path=target_path)

    print_section("instructions", output)
    print_reminder()


# ── CLI ─────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="context-db dispatcher")
    parser.add_argument(
        "command",
        choices=["init", "prompt", "pre-review", "review", "update", "maintain"],
    )
    parser.add_argument("prompt", nargs="?", default="")
    parser.add_argument("--mode", choices=["sub-agent", "main-agent", "ask"])
    parser.add_argument("--model", choices=["haiku", "sonnet", "opus", "ask"])
    parser.add_argument("--review-type", choices=["context-db", "full"])
    parser.add_argument("--config", default=".contextdb.json")
    parser.add_argument("--debug", action="store_true")

    args = parser.parse_args()

    if args.command == "init":
        cmd_init(args)
        return

    config = load_config(args.config)

    if args.command == "maintain":
        cmd_maintain(args, config)
        return

    if not args.prompt:
        print(f"No instruction provided. Ask the user what they want to "
              f"{args.command}.")
        print_reminder()
        return

    cmd_config = get_command_config(config, args.command)

    # CLI flags override config
    if args.mode:
        cmd_config["mode"] = args.mode
    if args.model:
        cmd_config["model"] = args.model
    if args.review_type:
        cmd_config["review-type"] = args.review_type

    mode = cmd_config["mode"]

    if mode == "main-agent":
        cmd_main_agent(args.command, args.prompt, cmd_config, args.debug)
    elif mode == "sub-agent":
        cmd_sub_agent(args.command, args.prompt, cmd_config, args.debug)
    elif mode == "ask":
        cmd_ask_mode(args.command, args.prompt, cmd_config, args.debug)


if __name__ == "__main__":
    main()
