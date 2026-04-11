#!/usr/bin/env python3
"""
context-db-agent.py — Context knowledge subagent.

Thin wrapper that calls claude -p with tools so the subagent model can
navigate context-db itself using the TOC script and Read tool — the same
B-tree navigation as the manual skill, but in an isolated context window.

The Python script does NOT read context-db files. The model does.

Modes:
  instructions — Read config, return tailored instructions for the main agent
  ask          — What should the developer know before starting this work?
  review       — Does this plan violate any project conventions?
  maintain     — Where should these learnings be filed?

Usage:
  context-db-agent.py instructions
  context-db-agent.py ask "<user prompt>"
  context-db-agent.py review "<coding plan>"
  context-db-agent.py maintain "<learnings from session>"

Dependencies: python3 (stdlib only), claude CLI
"""

import argparse
import json
import os
import subprocess
import sys

# ── Defaults ─────────────────────────────────────────────────────────────────

DEFAULT_CONFIG = {
    "modes": {
        "ask": {"model": "haiku", "behavior": "automatic", "frequency": "always"},
        "review": {"model": "sonnet", "behavior": "confirm"},
        "maintain": {"model": "sonnet", "behavior": "automatic"},
    }
}

# ── Instructions mode ──────────────────────────────────────────────────────
# Reads config, returns tailored instructions for the main agent.
# The main agent never needs to see .contextdb.json.


def _ask_block(config, script_path):
    """Generate the ask mode instruction block."""
    cfg = config["modes"].get("ask", {})
    behavior = cfg.get("behavior", "automatic")
    if behavior == "skip":
        return None

    frequency = cfg.get("frequency", "always")

    # When to call — frequency determines timing and skip rules
    if frequency == "always":
        when = "on every user prompt"
        skip_rule = None
    elif frequency == "new":
        when = "when the work shifts to a new topic"
        skip_rule = (
            "Skip follow-up prompts on the same topic "
            "(e.g. coding to documenting, feature work to git operations)."
        )
    else:  # major
        when = "for significant new prompts"
        skip_rule = "Skip small follow-ups and trivial requests."

    # How to behave — automatic vs confirm
    if behavior == "automatic":
        directive = f"You MUST run this {when}. Do not skip it, do not ask."
    else:  # confirm
        directive = f"Ask the user before running this. Run it {when}."

    if skip_rule:
        directive += f"\n{skip_rule}"

    return (
        f"## ask — before starting work\n"
        f"\n"
        f"Run:\n"
        f"  python3 {script_path} ask \"<the user's exact prompt>\"\n"
        f"\n"
        f"The response comes from a project knowledge expert. "
        f"It contains conventions, standards, and pitfalls relevant to "
        f"the user's prompt. Use it to inform your approach.\n"
        f"Wait for the response before taking other actions — do not "
        f"explore the codebase or start work in parallel.\n"
        f"The subagent reads the context-db/ folder for you. You can read "
        f"those files yourself if useful, but normally you do not need to.\n"
        f"{directive}"
    )


def _review_block(config, script_path):
    """Generate the review mode instruction block."""
    cfg = config["modes"].get("review", {})
    behavior = cfg.get("behavior", "automatic")
    if behavior == "skip":
        return None

    if behavior == "automatic":
        directive = (
            "You MUST run this before writing or modifying code — "
            "do not skip it, do not ask."
        )
    else:  # confirm
        directive = "Ask the user before running this."

    return (
        f"## review — before code changes\n"
        f"\n"
        f"After planning your approach but BEFORE writing any code, run:\n"
        f"  python3 {script_path} review \"<your implementation plan>\"\n"
        f"\n"
        f"The response comes from a project knowledge expert. "
        f"It is a review of your plan against project conventions — "
        f"violations to fix, pitfalls to avoid. "
        f"If it flags issues, fix your plan before proceeding.\n"
        f"{directive}"
    )


def _maintain_block(config, script_path):
    """Generate the maintain mode instruction block."""
    cfg = config["modes"].get("maintain", {})
    behavior = cfg.get("behavior", "automatic")
    if behavior == "skip":
        return None

    if behavior == "automatic":
        directive = (
            "You MUST run this after completing work — "
            "do not skip it, do not ask."
        )
    else:  # confirm
        directive = "Ask the user before running this."

    return (
        f"## maintain — after completing work\n"
        f"\n"
        f"After finishing a task, run:\n"
        f"  python3 {script_path} maintain \"<what you learned>\"\n"
        f"\n"
        f"Send corrections the user made, conventions you discovered, "
        f"pitfalls you hit. The expert will file them in the project "
        f"knowledge base. The response is a filing confirmation.\n"
        f"{directive}"
    )


def generate_instructions(config, script_path):
    """Generate directive instructions the main agent must follow."""
    blocks = []

    # Header
    blocks.append(
        "This project has a knowledge expert — a script that knows the "
        "project's conventions, standards, pitfalls, and design rationale.\n"
        "\n"
        "You MUST follow the instructions below."
    )

    # Build active mode blocks
    for builder in (_ask_block, _review_block, _maintain_block):
        block = builder(config, script_path)
        if block:
            blocks.append(block)

    # All skipped
    if all(
        config["modes"].get(m, {}).get("behavior") == "skip"
        for m in ("ask", "review", "maintain")
    ):
        blocks.append(
            "All expert modes are disabled. "
            "If you need project context, load /context-db-manual instead."
        )

    # Fallback
    blocks.append(
        "If the script fails, load /context-db-manual for direct "
        "context-db access."
    )

    return "\n\n".join(blocks)


# ── System prompts per mode ──────────────────────────────────────────────────
# Each mode gets a role + instructions to navigate context-db via the TOC
# script. The model reads the prompt, navigates the B-tree, reads relevant
# files, and responds.

ROLE_PROMPTS = {
    "ask": """\
You are a project knowledge expert. Return ONLY bullet points of relevant
project knowledge. Nothing else.

Only return information found in the context-db/ folder. Do not return
information about context-db itself — its structure, maintenance, or operation.
Only return project knowledge relevant to the developer's work.

If nothing is relevant, respond: No relevant project context.

Never write code. Never answer the prompt. Never ask questions.
Only return knowledge from the files you read.""",

    "review": """\
You are a project knowledge expert. Check the plan against project conventions.

Respond with:
- VIOLATION: [what the plan does wrong] — convention: [the rule]
- WARNING: [pitfall the plan doesn't account for]

If no issues: No convention issues found.

Never help implement the plan. Only flag convention problems.""",

    "maintain": """\
You are maintaining a project knowledge base. Determine where to file the
learnings below.

Respond with:
ACTION: update|create|skip
FILE: path/to/file.md
CONTENT:
[content to add]

If skipping:
ACTION: skip
REASON: [why this doesn't belong]

Rules:
- Only file what the code can't tell you (conventions, pitfalls, corrections)
- Update existing files when they cover the topic
- Create new files only for genuinely new topics""",
}

# Content first, then navigation instructions
USER_MSG_TEMPLATES = {
    "ask": """\
Developer's prompt: {prompt}

Now navigate the project knowledge base to find relevant conventions,
standards, pitfalls, and context. Use the TOC script to browse:
  {toc_script} {context_db}
Read descriptions at each level. Drill into relevant folders. Read matching
files. Return what applies to the prompt above.""",

    "review": """\
Plan to review:
{prompt}

Now navigate the project knowledge base to find conventions and standards
that apply. Use the TOC script to browse:
  {toc_script} {context_db}
Read descriptions at each level. Drill into relevant folders. Read matching
files. Flag any violations of the conventions you find.""",

    "maintain": """\
Learnings to file:
{prompt}

Now navigate the project knowledge base to understand its structure. Use the
TOC script to browse:
  {toc_script} {context_db}
Determine where these learnings should be filed.""",
}


# ── Config ───────────────────────────────────────────────────────────────────


def load_config(config_path):
    """Load .contextdb.json, merge with defaults."""
    config = json.loads(json.dumps(DEFAULT_CONFIG))
    if os.path.exists(config_path):
        with open(config_path) as f:
            user_config = json.load(f)
        if "modes" in user_config:
            for mode, settings in user_config["modes"].items():
                if mode in config["modes"]:
                    config["modes"][mode].update(settings)
                else:
                    config["modes"][mode] = settings
    return config


def config_summary(config):
    """One-line summary of active config for the reminder footer."""
    parts = []
    for mode in ("ask", "review", "maintain"):
        if mode in config["modes"]:
            behavior = config["modes"][mode].get("behavior", "automatic")
            parts.append(f"{mode}={behavior}")
    return ", ".join(parts)


# ── TOC script discovery ────────────────────────────────────────────────────


def find_toc_script():
    """Find context-db-generate-toc.sh relative to this script."""
    from pathlib import Path

    script_dir = Path(__file__).resolve().parent
    skills_dir = script_dir.parent.parent

    for candidate in [
        skills_dir / "context-db-manual" / "scripts" / "context-db-generate-toc.sh",
        Path(__file__).parent.parent.parent / "context-db-manual" / "scripts" / "context-db-generate-toc.sh",
    ]:
        if candidate.exists():
            return str(candidate)

    # Fallback — assume standard install location
    return ".claude/skills/context-db-manual/scripts/context-db-generate-toc.sh"


# ── Script path detection ──────────────────────────────────────────────────


def detect_script_path():
    """Detect the path to this script, for use in generated instructions."""
    from pathlib import Path

    # Try symlink-relative path first (preserves .claude/ structure)
    script_dir_sym = Path(__file__).parent
    candidate_sym = script_dir_sym / "context-db-agent.py"
    if candidate_sym.exists():
        return str(candidate_sym)

    # Then resolved path
    script_dir = Path(__file__).resolve().parent
    candidate = script_dir / "context-db-agent.py"
    if candidate.exists():
        return str(candidate)

    return ".claude/skills/context-db-subagent/scripts/context-db-agent.py"


# ── Main ─────────────────────────────────────────────────────────────────────


def run_instructions(args):
    """Print tailored instructions for the main agent based on config."""
    config = load_config(args.config)
    script_path = detect_script_path()
    print(generate_instructions(config, script_path))


def run_subagent(args):
    """Call the subagent for ask/review/maintain modes."""
    # Validate context-db exists
    if not os.path.isdir(args.context_db):
        print(f"Error: context-db not found: {args.context_db}", file=sys.stderr)
        sys.exit(1)

    # Load config
    config = load_config(args.config)
    model = args.model or config["modes"][args.mode]["model"]

    # Find TOC script
    toc_script = args.toc_script or find_toc_script()

    # System prompt: role only
    system_prompt = ROLE_PROMPTS[args.mode]

    # User message: content first, then navigation instructions
    user_msg = USER_MSG_TEMPLATES[args.mode].format(
        prompt=args.prompt,
        toc_script=toc_script,
        context_db=args.context_db,
    )

    # Call claude with tools so the model can navigate context-db itself
    cmd = [
        "claude", "-p",
        "--model", model,
        "--tools", "Bash,Read",
        "--no-session-persistence",
        "--permission-mode", "bypassPermissions",
        "--system-prompt", system_prompt,
    ]

    env = os.environ.copy()
    env["CONTEXT_DB_SUBAGENT"] = "1"

    try:
        result = subprocess.run(
            cmd, input=user_msg,
            capture_output=True, text=True, timeout=180, env=env,
        )
    except subprocess.TimeoutExpired:
        print("Error: subagent timed out", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("Error: 'claude' not found. Is Claude Code installed?",
              file=sys.stderr)
        sys.exit(1)

    if result.returncode != 0:
        print(f"Error: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    # Output with mode tag and reminder footer
    cfg = config_summary(config)
    mode_label = {
        "ask": "project context",
        "review": "plan review",
        "maintain": "filing recommendation",
    }
    print(f"[context-db {args.mode}] {mode_label[args.mode]}\n")
    print(result.stdout.strip())
    print(
        f"\n---\n"
        f"context-db-agent: Call me with 'ask' before starting work, "
        f"'review' before code changes, 'maintain' after completing work.\n"
        f"Config: {cfg}"
    )


def main():
    parser = argparse.ArgumentParser(
        description="context-db subagent — project knowledge expert",
    )
    parser.add_argument(
        "mode", choices=["instructions", "ask", "review", "maintain"],
        help="instructions | ask | review | maintain",
    )
    parser.add_argument("prompt", nargs="?", default="",
                        help="The prompt to process (not used for instructions)")
    parser.add_argument("--model", help="Override model (default from config)")
    parser.add_argument("--context-db", default="context-db/",
                        help="Path to context-db folder")
    parser.add_argument("--config", default=".contextdb.json",
                        help="Path to config file")
    parser.add_argument("--session-id", help="Session ID (reserved for future)")
    parser.add_argument("--toc-script", help="Path to TOC script (auto-detected)")

    args = parser.parse_args()

    if args.mode == "instructions":
        run_instructions(args)
    else:
        if not args.prompt:
            parser.error(f"{args.mode} mode requires a prompt argument")
        run_subagent(args)


if __name__ == "__main__":
    main()
