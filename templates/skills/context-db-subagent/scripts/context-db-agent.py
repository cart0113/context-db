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
        f"The response comes from a project knowledge expert who knows this "
        f"project's conventions, design decisions, gotchas, and standards. "
        f"Treat it as a starting point — a map and hints, not the final "
        f"answer. Use it to orient your approach, then verify against the "
        f"actual code.\n"
        f"Wait for the response before taking other actions — do not "
        f"explore the codebase or start work in parallel.\n"
        f"The expert reads the project knowledge base for you. You can read "
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
You are a project knowledge lookup service.

Your working directory is a B-tree of markdown files (~100 lines each). Navigate
it using ONLY these steps:
1. Run: bash {toc_script} .
   This lists subfolders and files with descriptions from their YAML frontmatter.
2. Pick what's relevant to the developer's prompt.
   - If it's a folder, run: bash {toc_script} <subfolder>/
   - If it's a file, read the whole file.
3. Repeat until you've found what applies.

Do not use find, grep, or ls. Only the TOC script and Read.
All files are relative to your cwd (.). The TOC script is an external tool —
never read files from its directory.
Never write code. Never answer the prompt. Never help with the task.
Only return knowledge from the files you read.
If nothing is relevant, respond: No relevant project context.""",

    "review": """\
You are a project knowledge lookup service. Check the plan against project
conventions found in your working directory.

To navigate, run: bash {toc_script} .
This lists subfolders and files with descriptions from their YAML frontmatter.
Drill into relevant folders: bash {toc_script} <subfolder>/
Then read the files that match.

Respond with:
- VIOLATION: [what the plan does wrong] — convention: [the rule]
- WARNING: [pitfall the plan doesn't account for]

If no issues: No convention issues found.

Never help implement the plan. Only flag convention problems.""",

    "maintain": """\
You are maintaining a knowledge base. Your working directory contains the
markdown files.

To navigate, run: bash {toc_script} .
This lists subfolders and files with descriptions from their YAML frontmatter.
Drill into relevant folders: bash {toc_script} <subfolder>/

Determine where to file the learnings below.

Respond with:
ACTION: update|create|skip
FILE: path/to/file.md
CONTENT:
[content to add]

Rules:
- Only file what the code can't tell you (conventions, pitfalls, corrections)
- Update existing files when they cover the topic
- Create new files only for genuinely new topics""",
}

USER_MSG_TEMPLATES = {
    "ask": """\
Use this knowledge base to provide the best, most useful context for this \
developer prompt:

"{prompt}"
""",

    "review": """\
Review this implementation plan against project conventions:

"{prompt}"
""",

    "maintain": """\
File these learnings:

"{prompt}"
""",
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


def find_toc_script(context_db_path=None):
    """Find context-db-generate-toc.sh — check project .claude/ first."""
    from pathlib import Path

    toc_name = "context-db-manual/scripts/context-db-generate-toc.sh"

    # 1. Relative to project root (.claude/skills/) — works whether cwd is
    #    project root or context-db/ (one level up)
    candidates = []
    if context_db_path:
        project_root = Path(context_db_path).resolve().parent
        candidates.append(project_root / ".claude" / "skills" / toc_name)
    candidates.append(Path.cwd() / ".claude" / "skills" / toc_name)
    candidates.append(Path.cwd().parent / ".claude" / "skills" / toc_name)

    # 2. Relative to this script (follows symlinks back to templates)
    script_dir = Path(__file__).resolve().parent
    skills_dir = script_dir.parent.parent
    candidates.append(skills_dir / toc_name)

    for candidate in candidates:
        if candidate.exists():
            return str(candidate.resolve())

    # Fallback — assume standard install location
    return ".claude/skills/" + toc_name


# ── Script path detection ──────────────────────────────────────────────────


def detect_script_path():
    """Detect the path to this script, for use in generated instructions."""
    from pathlib import Path

    # Try symlink-relative path first (preserves .claude/ structure)
    # Normalize to collapse ../  (e.g. hooks/../skills → skills)
    script_dir_sym = Path(os.path.normpath(Path(__file__).parent))
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
    # Resolve context-db to absolute path — we'll cd into it
    context_db = os.path.abspath(args.context_db)
    if not os.path.isdir(context_db):
        print(f"Error: context-db not found: {context_db}", file=sys.stderr)
        sys.exit(1)

    # Load config
    config = load_config(args.config)
    model = args.model or config["modes"][args.mode]["model"]

    # Find TOC script — resolve to absolute since we'll change cwd
    toc_script = os.path.abspath(args.toc_script or find_toc_script())

    # System prompt includes TOC path; user message is just the prompt
    system_prompt = ROLE_PROMPTS[args.mode].format(toc_script=toc_script)
    user_msg = USER_MSG_TEMPLATES[args.mode].format(prompt=args.prompt)

    # Debug: print full prompts and exit when --debug is set
    if args.debug:
        print("=== SYSTEM PROMPT ===", flush=True)
        print(system_prompt, flush=True)
        print("\n=== USER MESSAGE ===", flush=True)
        print(user_msg, flush=True)
        print("=====================", flush=True)
        return

    # Call claude from inside context-db/ — no rules, no skills, just markdown
    cmd = [
        "claude", "-p",
        "--model", model,
        "--tools", "Bash,Read",
        "--output-format", "stream-json",
        "--verbose",
        "--no-session-persistence",
        "--permission-mode", "bypassPermissions",
        "--system-prompt", system_prompt,
        "--bare",
    ]

    # Print full details for visibility
    cmd_display = [c if c != system_prompt else '"<system prompt>"' for c in cmd]
    print(f"[context-db {args.mode}] cwd={context_db}", flush=True)
    print(f"[context-db {args.mode}] {' '.join(cmd_display)}", flush=True)
    print(f"\n--- system prompt ---\n{system_prompt}\n--- end system prompt ---", flush=True)
    print(f"\n--- user message ---\n{user_msg}\n--- end user message ---\n", flush=True)

    env = os.environ.copy()
    env["CONTEXT_DB_SUBAGENT"] = "1"

    # Stream output: read stream-json events, print tool activity live
    import time as _time
    start_time = _time.time()
    final_text = ""
    cost_usd = 0.0
    total_input = 0
    total_output = 0
    try:
        proc = subprocess.Popen(
            cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True, env=env,
            cwd=context_db,
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
            if etype == "assistant":
                # Print tool calls as they happen for visibility
                for block in event.get("message", {}).get("content", []):
                    if block.get("type") == "tool_use":
                        tool = block.get("name", "")
                        inp = block.get("input", {})
                        if tool == "Read":
                            print(f"  reading: {inp.get('file_path', '')}", flush=True)
                        elif tool == "Bash":
                            print(f"  running: {inp.get('command', '')}", flush=True)
                # Track token usage from assistant messages
                usage = event.get("message", {}).get("usage", {})
                total_input += usage.get("input_tokens", 0)
                total_output += usage.get("output_tokens", 0)
            elif etype == "result":
                final_text = event.get("result", "")
                cost_usd = event.get("total_cost_usd", 0.0)
                if args.debug:
                    print(f"  [debug result keys: {list(event.keys())}]", flush=True)

        proc.wait(timeout=180)
        stderr_out = proc.stderr.read()
    except subprocess.TimeoutExpired:
        proc.kill()
        print("Error: subagent timed out", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("Error: 'claude' not found. Is Claude Code installed?",
              file=sys.stderr)
        sys.exit(1)

    if proc.returncode != 0:
        print(f"Error: {stderr_out}", file=sys.stderr)
        sys.exit(1)

    elapsed = _time.time() - start_time

    # Demarcated output — context for the main agent, then metadata
    print(f"\n--- context for prompt ---")
    print(final_text.strip())
    print(f"--- end context ---")
    print(f"\n--- metadata ---")
    print(f"model: {model} | cost: ${cost_usd:.4f} | "
          f"tokens: {total_input}in/{total_output}out | "
          f"time: {elapsed:.1f}s")
    print(f"config: {config_summary(config)}")
    print(f"--- end metadata ---", flush=True)


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
    parser.add_argument("--context-db", default=".",
                        help="Path to context-db folder (default: current directory)")
    parser.add_argument("--config", default=".contextdb.json",
                        help="Path to config file")
    parser.add_argument("--session-id", help="Session ID (reserved for future)")
    parser.add_argument("--toc-script", help="Path to TOC script (auto-detected)")
    parser.add_argument("--debug", action="store_true",
                        help="Print full prompts before calling the subagent")

    args = parser.parse_args()

    if args.mode == "instructions":
        run_instructions(args)
    else:
        if not args.prompt:
            parser.error(f"{args.mode} mode requires a prompt argument")
        run_subagent(args)


if __name__ == "__main__":
    main()
