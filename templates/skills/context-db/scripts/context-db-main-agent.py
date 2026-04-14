#!/usr/bin/env python3
"""
context-db-main-agent.py — dispatcher for /context-db skill.

Called by the main agent via SKILL.md. Reads config, determines mode, and
prints tagged output sections for the agent to follow.

Run with --help or <command> --help for usage.

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
    """Load context-db.json, merge with defaults."""
    config = json.loads(json.dumps(DEFAULT_CONFIG))
    if os.path.exists(config_path):
        with open(config_path) as f:
            user = json.load(f)
        if "defaults" in user:
            config["defaults"].update(user["defaults"])
        for cmd in COMMANDS:
            if cmd in user:
                config[cmd].update(user[cmd])
        if "init" in user:
            config["init"] = user["init"]
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
    """Load a prompt template from the prompts/main-agent/ directory."""
    prompts_dir = Path(__file__).resolve().parent / "prompts" / "main-agent"
    path = prompts_dir / f"{name}.md"
    if not path.exists():
        sys.exit(f"Error: template not found: {path}")
    return path.read_text()


def fill_template(template, **kwargs):
    """Fill {variables} in a template. Unknown variables are left as-is."""
    for key, value in kwargs.items():
        template = template.replace(f"{{{key}}}", str(value))
    return template


# ── Output helpers ─────────────────────────────────────────────────────────


def print_template(name, **kwargs):
    """Load a template, fill variables, and print. Tags are in the file."""
    print()
    print(fill_template(load_template(name), **kwargs))


def print_section(tag, content):
    """Print a dynamically tagged section (for content not from templates)."""
    print(f"\n[{tag}]\n")
    print(content.strip())
    print(f"\n[end {tag}]")


# ── Command handlers ────────────────────────────────────────────────────────


def cmd_init(args, config):
    """Print startup instructions for the main agent."""
    print(load_template("init-instructions").strip())

    init_config = config.get("init", {})
    load_manual = init_config.get("load-manual", False)
    if load_manual:
        scope = load_manual if isinstance(load_manual, str) else "all"
        print()
        _print_load_manual(scope)


def cmd_load_manual(args):
    """Print context-db reading/writing instructions into the agent's context."""
    if args.read and not args.write:
        scope = "read"
    elif args.write and not args.read:
        scope = "write"
    else:
        scope = "all"
    _print_load_manual(scope)


def _print_load_manual(scope):
    """Print load-manual content for the given scope."""
    toc = find_toc_script()
    context_db_rel = find_context_db()

    if scope in ("all", "read"):
        print_template("read-mechanics", toc=toc, context_db_rel=context_db_rel)
        print_template("context-usage")

    if scope in ("all", "write"):
        print_template("write-file-format", toc=toc,
                        context_db_rel=context_db_rel)
        print_template("write-content-guide")


def cmd_main_agent(command, prompt, cmd_config, debug=False):
    """Print instructions for the main agent to navigate context-db directly."""
    toc = find_toc_script()
    context_db_rel = find_context_db()

    if debug:
        print(f"mode: main-agent")
        print(f"context-db: {context_db_rel}/")
        print(f"toc: {toc}")

    if command == "update":
        print_template("write-mechanics", toc=toc,
                        context_db_rel=context_db_rel)
        print_template("write-file-format", toc=toc,
                        context_db_rel=context_db_rel)
        print_template("memory-not-vendor")
        print_template("update-general",
                        context_db_rel=context_db_rel)
        if prompt:
            print_section("update-user-instructions", prompt)
    else:
        # Read commands: prompt, pre-review, review
        print_template("read-mechanics", toc=toc, context_db_rel=context_db_rel)
        print_template("context-usage")
        print_template(command)
        if prompt:
            print_section(f"{command}-user-instructions", prompt)


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



def cmd_maintain(args, config):
    """Print the full 7-phase maintain instructions."""
    toc = find_toc_script()
    context_db_rel = find_context_db()
    target_path = args.path if args.path else f"{context_db_rel}/"

    print_template("write-mechanics", toc=toc, context_db_rel=context_db_rel)
    print_template("write-file-format", toc=toc, context_db_rel=context_db_rel)
    print_template("write-content-guide")
    print_template("maintain-instructions", toc=toc,
                    context_db_rel=context_db_rel, target_path=target_path)



# ── CLI ─────────────────────────────────────────────────────────────────────

MODE_CHOICES = ["sub-agent", "main-agent", "ask"]
MODEL_CHOICES = ["haiku", "sonnet", "opus", "ask"]


def add_mode_flags(sub):
    """Add --mode, --model, --debug, --config to a subparser."""
    sub.add_argument("--mode", choices=MODE_CHOICES)
    sub.add_argument("--model", choices=MODEL_CHOICES)
    sub.add_argument("--config", default="context-db.json")
    sub.add_argument("--debug", action="store_true")


def dispatch_command(args, config):
    """Route a prompt/pre-review/review/update command by mode."""
    command = args.command
    prompt = args.instruction

    if not prompt and command != "update":
        print(f"No instruction provided. Ask the user what they want to "
              f"{command}.")
    
        return

    cmd_config = get_command_config(config, command)

    if args.mode:
        cmd_config["mode"] = args.mode
    if args.model:
        cmd_config["model"] = args.model
    if hasattr(args, "review_type") and args.review_type:
        cmd_config["review-type"] = args.review_type

    mode = cmd_config["mode"]

    if mode == "main-agent":
        cmd_main_agent(command, prompt, cmd_config, args.debug)
    elif mode == "sub-agent":
        cmd_sub_agent(command, prompt, cmd_config, args.debug)
    elif mode == "ask":
        cmd_ask_mode(command, prompt, cmd_config, args.debug)


def main():
    parser = argparse.ArgumentParser(
        prog="context-db",
        description="Project knowledge base",
    )
    subs = parser.add_subparsers(dest="command")

    # init
    subs.add_parser("init", help="Startup instructions")

    # load-manual
    lm = subs.add_parser("load-manual",
                         help="Load reading/writing instructions into context")
    lm.add_argument("--read", action="store_true",
                    help="Only reading instructions")
    lm.add_argument("--write", action="store_true",
                    help="Only writing instructions")

    # prompt
    p = subs.add_parser("prompt", help="Consult knowledge base")
    p.add_argument("instruction", nargs="?", default="")
    add_mode_flags(p)

    # pre-review
    pr = subs.add_parser("pre-review",
                         help="Check plan against standards before implementing")
    pr.add_argument("instruction", nargs="?", default="")
    add_mode_flags(pr)

    # review
    rv = subs.add_parser("review",
                         help="Review changes against conventions")
    rv.add_argument("instruction", nargs="?", default="")
    rv.add_argument("--review-type", choices=["context-db", "full"])
    add_mode_flags(rv)

    # update
    up = subs.add_parser("update", help="File learnings into context-db")
    up.add_argument("instruction", nargs="?", default="")
    add_mode_flags(up)

    # maintain
    mt = subs.add_parser("maintain", help="Audit and maintain context-db")
    mt.add_argument("path", nargs="?", default="")
    mt.add_argument("--config", default="context-db.json")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    config = load_config(
        args.config if hasattr(args, "config") else "context-db.json"
    )

    if args.command == "init":
        cmd_init(args, config)
    elif args.command == "load-manual":
        cmd_load_manual(args)
    elif args.command == "maintain":
        cmd_maintain(args, config)
    else:
        dispatch_command(args, config)


if __name__ == "__main__":
    main()
