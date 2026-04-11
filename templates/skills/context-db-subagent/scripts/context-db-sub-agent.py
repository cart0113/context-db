#!/usr/bin/env python3
"""
context-db-sub-agent.py — project knowledge subagent.

Calls claude -p from inside context-db/ so the model navigates the B-tree
itself using the TOC script and Read tool. The main agent's context window
stays clean.

Modes:
  instructions       Print directives for the main agent (from .contextdb.json)
  ask                What should the developer know before starting this work?
  review             Does this plan violate any project conventions?
  update-context-db  File learnings into context-db, then review changes

Usage:
  context-db-sub-agent.py instructions
  context-db-sub-agent.py instructions --brief
  context-db-sub-agent.py instructions --ask-when always --review-when never
  context-db-sub-agent.py ask "user prompt"
  context-db-sub-agent.py ask "prompt" --debug
  context-db-sub-agent.py update-context-db "what was learned" --debug

Dependencies: python3 (stdlib only), claude CLI
"""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

# ── Config ──────────────────────────────────────────────────────────────────

MODES = ["ask", "review", "update-context-db"]

DEFAULT_CONFIG = {
    "ask": {"model": "haiku", "when": "major"},
    # scope: "context-db-only" = only flag issues backed by context-db conventions
    #        "context-db-and-general" = also do a general code review
    "review": {"model": "sonnet", "when": "major", "scope": "context-db-only"},
    "update-context-db": {
        "model": "sonnet",
        "when": "major",
        "review": {"enabled": True, "model": "sonnet"},
    },
    "reinforce_subagent_rules": True,
}

# Tools granted to each mode's subagent
MODE_TOOLS = {
    "ask": "Bash,Read",
    "review": "Bash,Read",
    "update-context-db": "Bash,Read,Write,Edit",
}



def load_config(config_path):
    """Load .contextdb.json, merge with defaults."""
    config = json.loads(json.dumps(DEFAULT_CONFIG))
    if os.path.exists(config_path):
        with open(config_path) as f:
            user = json.load(f)
        for mode in MODES:
            if mode in user:
                for key, val in user[mode].items():
                    if isinstance(val, dict) and isinstance(
                        config[mode].get(key), dict
                    ):
                        config[mode][key].update(val)
                    else:
                        config[mode][key] = val
        if "reinforce_subagent_rules" in user:
            config["reinforce_subagent_rules"] = user["reinforce_subagent_rules"]
    return config


# ── Path discovery ──────────────────────────────────────────────────────────


def find_toc_script():
    """Find context-db-generate-toc.sh."""
    toc = "context-db-manual/scripts/context-db-generate-toc.sh"
    for base in [
        Path.cwd() / ".claude" / "skills",
        Path.cwd().parent / ".claude" / "skills",
        Path(__file__).resolve().parent.parent.parent,
    ]:
        candidate = base / toc
        if candidate.exists():
            return str(candidate.resolve())
    return ".claude/skills/" + toc


def find_script_path():
    """Find this script's path for use in generated instructions."""
    normalized = (
        Path(os.path.normpath(Path(__file__).parent)) / "context-db-sub-agent.py"
    )
    if normalized.exists():
        return str(normalized)
    resolved = Path(__file__).resolve()
    if resolved.exists():
        return str(resolved)
    return ".claude/skills/context-db-subagent/scripts/context-db-sub-agent.py"


def find_context_db():
    """Find context-db/. Works from project root or inside context-db/."""
    if os.path.isdir("context-db"):
        return os.path.abspath("context-db")
    return os.path.abspath(".")


def find_project_root(context_db):
    """Find git project root from context-db path."""
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        cwd=context_db,
    )
    if result.returncode == 0:
        return result.stdout.strip()
    # Fallback: assume context-db is one level below project root
    return os.path.dirname(context_db)


# ── Instructions mode ───────────────────────────────────────────────────────


# Per-mode "when" descriptions — what "major" means for each mode
ASK_WHEN = {
    "always": "Run this on every new user prompt. Do not skip it, do not ask.",
    "major": (
        "Run this when the user's prompt introduces significant new work or "
        "the topic has changed (e.g. was writing code, now asked to write docs "
        "or commit). Skip follow-ups, small refinements, and clarifications "
        "on the same topic."
    ),
}
REVIEW_WHEN = {
    "always": "Run this after every code change. Do not skip it, do not ask.",
    "major": (
        "Run this after significant code changes — new features, API changes, "
        "new files, architectural decisions. Skip single-line fixes, renames, "
        "formatting, and changes you are confident about from a prior ask."
    ),
}
UPDATE_WHEN = {
    "always": "Run this after every completed task. Do not skip it, do not ask.",
    "major": (
        "Run this when important information came up during the session that "
        "future agents should know — user corrections, discovered conventions, "
        "surprising pitfalls. Skip routine work where nothing new was learned."
    ),
}

# Brief versions for the reminder section
ASK_BRIEF = {
    "always": "on every new user prompt",
    "major": "when work changes topic or scope (skip follow-ups and small refinements)",
}
REVIEW_BRIEF = {
    "always": "after every code change",
    "major": "after significant changes (skip small fixes, renames, formatting)",
}
UPDATE_BRIEF = {
    "always": "after every completed task",
    "major": "when you learned something future agents should know (skip routine work)",
}


def generate_instructions(config, script_path):
    """Generate directives at system-prompt authority level. This is where
    behavioral rules must live — tool result instructions (Priority 30)
    get deprioritized by the model. These instructions (Priority 0-10)
    are what the agent actually follows."""
    blocks = [
        "This project has a context agent. You MUST follow the instructions "
        "below."
    ]

    # ask
    when = config["ask"].get("when", "major")
    if when != "never":
        blocks.append(
            f"## ask — before starting work\n\n"
            f"When: {ASK_WHEN[when]}\n\n"
            f"Run (timeout 120000ms):\n"
            f"  python3 {script_path} ask \"<the user's exact prompt>\"\n\n"
            f"Wait for the response before taking other actions."
        )

    # review
    when = config["review"].get("when", "major")
    if when != "never":
        blocks.append(
            f"## review — after code changes\n\n"
            f"When: {REVIEW_WHEN[when]}\n\n"
            f"Before making code changes:\n"
            f"  If the repo has uncommitted changes, ask the user whether "
            f"they'd like you to commit or if they will, to get a clean "
            f"baseline.\n\n"
            f"After making your code changes, run:\n"
            f"  python3 {script_path} review \"<summary of changes made>\"\n\n"
            f"The review response may have been generated by a less capable "
            f"model — treat it as advisory. Evaluate each item yourself, "
            f"fix real issues, and ignore false positives."
        )

    # update-context-db
    when = config["update-context-db"].get("when", "major")
    if when != "never":
        review_cfg = config["update-context-db"].get("review", {})
        review_enabled = review_cfg.get("enabled", True)

        if review_enabled:
            blocks.append(
                f"## update-context-db — after completing work\n\n"
                f"When: {UPDATE_WHEN[when]}\n\n"
                f"This mode has two phases: a subagent updates context-db, "
                f"then a review subagent checks the changes.\n\n"
                f"Before running:\n"
                f"  1. Commit any pending changes so the git diff is clean.\n\n"
                f"Run:\n"
                f"  python3 {script_path} update-context-db "
                f"\"<what you learned>\"\n\n"
                f"The review response may have been generated by a less "
                f"capable model — treat it as advisory. Evaluate each item "
                f"yourself, fix real issues in context-db, and ignore false "
                f"positives."
            )
        else:
            blocks.append(
                f"## update-context-db — after completing work\n\n"
                f"When: {UPDATE_WHEN[when]}\n\n"
                f"Run:\n"
                f"  python3 {script_path} update-context-db "
                f"\"<what you learned>\""
            )

    # How to handle responses
    response_rules = []
    if config["ask"].get("when", "major") != "never":
        response_rules.append(
            "When the ask response comes back: this is a starting point, "
            "not a final answer. Trust but verify — corroborate key claims "
            "against the actual code, docs, or other project assets before "
            "answering. Follow any project standards it returns."
        )
    if config["review"].get("when", "major") != "never":
        response_rules.append(
            "When the review response comes back: this is feedback for "
            "your consideration, not an order. Verify it makes sense, fix "
            "real issues, and use your judgment."
        )
    if response_rules:
        blocks.append(
            "## How to handle responses\n\n" + "\n".join(response_rules)
        )

    blocks.append("If the script fails, tell the user and stop working.")
    return "\n\n".join(blocks)


def generate_brief(config, script_path):
    """Self-contained reminder with commands. Appended to every response
    so the main agent can act on it without remembering session start.
    Includes review flow guidance — not just the command."""
    lines = ["context-db-sub-agent reminder:"]

    when = config["ask"].get("when", "major")
    if when != "never":
        lines.append("")
        lines.append(f"ask — {ASK_BRIEF[when]}:")
        lines.append(f"  python3 {script_path} ask \"<prompt>\"")

    when = config["review"].get("when", "major")
    if when != "never":
        lines.append("")
        lines.append(f"review — {REVIEW_BRIEF[when]}:")
        lines.append(f"  1. Ensure repo was committed before your changes")
        lines.append(
            f"  2. python3 {script_path} review \"<summary of changes>\""
        )
        lines.append(f"  3. Evaluate response (advisory), fix real issues")

    when = config["update-context-db"].get("when", "major")
    if when != "never":
        review_cfg = config["update-context-db"].get("review", {})
        review_enabled = review_cfg.get("enabled", True)

        lines.append("")
        lines.append(f"update-context-db — {UPDATE_BRIEF[when]}:")
        if review_enabled:
            lines.append(f"  1. Commit pending changes first")
            lines.append(
                f"  2. python3 {script_path} update-context-db \"<learnings>\""
            )
            lines.append(f"  3. Evaluate review response (advisory), fix real issues")
        else:
            lines.append(
                f"  python3 {script_path} update-context-db \"<learnings>\""
            )

    return "\n".join(lines)


# ── System prompts ──────────────────────────────────────────────────────────

SYSTEM_PROMPTS = {
    "ask": """\
You are a project knowledge lookup service.

Your working directory is a B-tree of markdown files (~100 lines each). Navigate
it using ONLY these steps:
1. Run: bash {toc} .
   This lists subfolders and files with descriptions from their YAML frontmatter.
2. Pick what's relevant to the developer's prompt.
   - If it's a folder, run: bash {toc} <subfolder>/
   - If it's a file, read the whole file.
3. Repeat until you've found what applies.

Do not use find, grep, or ls. Only the TOC script and Read.
All files are relative to your cwd (.). The TOC script is an external tool —
never read files from its directory.
Never write code. Never answer the prompt. Never help with the task.

Return your findings as a list of verbatim snippets. For each relevant section:
1. One line explaining why this snippet is relevant.
2. The exact text from the file, wrapped in markers:

[context-db/path/to/file.md:START-END]
exact file content, copied verbatim
[end]

Do not summarize or paraphrase file content. Quote it exactly.
If nothing is relevant, respond: No relevant project context.""",
    # Review prompt is built dynamically by build_review_prompt() based on scope.
    # This entry is kept as a placeholder; run_review() does not use it.
    "review": None,
    "update-context-db": """\
You are maintaining a knowledge base in your working directory ({cwd}).

Navigate using ONLY:
1. Run: bash {toc} .
2. Drill into folders: bash {toc} <subfolder>/
3. Read matching files to understand what already exists.

Then make your changes directly:
- Use Edit to update existing files that cover the topic.
- Use Write to create new files only for genuinely new topics.
- Use absolute paths for all file operations (your cwd is {cwd}).
- Follow the format of existing files (YAML frontmatter with name and
  description fields, content in markdown).

Rules:
- Only file what the code can't tell you.
- Update existing files before creating new ones.
- Keep files around 100 lines.

When done, summarize what you changed and why.""",
}

USER_PROMPTS = {
    "ask": (
        "Use this knowledge base to provide the best, most useful context "
        'for this developer prompt:\n\n"{prompt}"'
    ),
    "review": (
        "Review these changes against project conventions:"
        '\n\n"{prompt}"'
    ),
    "update-context-db": 'File these learnings:\n\n"{prompt}"',
}

def build_review_prompt(toc, context_db_rel, scope):
    """Build the review system prompt based on scope config.

    scope: "context-db-only"      — only flag issues backed by context-db
           "context-db-and-general" — also do a general code review
    """
    base = f"""\
You are a code review service. Your working directory is the project root.

Steps:
1. Run: git diff
   to see what was changed.
2. Navigate the project knowledge base for relevant conventions:
   Run: bash {toc} {context_db_rel}/
   Drill into folders: bash {toc} {context_db_rel}/<subfolder>/
   Read files that might contain relevant standards or pitfalls.
3. Review the changes against the conventions you found.

Write a full, human-readable review report. For each issue:
- Describe the problem clearly.
- Quote the relevant snippet from the context-db file that supports your
  critique, with its source path:

  Source: {context_db_rel}/path/to/file.md
  > exact quoted text from the convention file

If no convention issues are found, say so clearly."""

    if scope == "context-db-and-general":
        base += """

After the convention review, also perform a general code review using your own
expertise. Flag anything that looks wrong, risky, or could be improved —
regardless of whether it appears in the knowledge base.

Clearly separate the two sections in your report:
  ## Convention Issues (from context-db)
  ## General Code Review"""
    else:
        base += """

Only flag issues supported by conventions in the knowledge base. Do not add
general code review opinions — if it's not in context-db, don't flag it."""

    base += """

Never suggest fixes — only identify problems."""
    return base


REVIEW_UPDATE_PROMPT = """\
You are reviewing changes made to a project knowledge base (context-db/).

You will receive the learnings that were filed and a git diff of all changes.
Perform a thorough review:

1. ACCURACY — Read the project's source code, docs, and other files to verify
   the knowledge is correct. Flag anything that contradicts what's in the code.
2. REDUNDANCY — Read other files in context-db/ to check if this information
   is already covered elsewhere. Flag duplication.
3. STRUCTURE — Check context-db conventions: YAML frontmatter with name and
   description fields, files ~100 lines, logical folder placement.
4. VALUE — Is this knowledge that code can't tell you? Flag entries that just
   restate what's obvious from reading the source.
5. COMPLETENESS — Did the update miss anything important from the learnings?

Your working directory is the project root. context-db/ is a subdirectory.
You can Read any file in the project to verify claims.

For each issue found:
  ISSUE: [category] — [description]
  FILE: [path]
  SUGGESTION: [what to fix]

If everything looks good:
  APPROVED — [brief summary of why the changes are sound]

Be thorough but fair. Minor style nits are not issues."""


# ── Subagent execution ─────────────────────────────────────────────────────


def spawn_claude(system_prompt, user_msg, model, tools, cwd, debug=False):
    """Run claude -p subprocess and return (response_text, cost_usd, elapsed).

    Returns (None, 0.0, elapsed) on timeout so the caller can decide how
    to handle it (fatal for update, non-fatal for review).
    """
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
        "--bare",
    ]

    env = {**os.environ, "CONTEXT_DB_SUBAGENT": "1"}
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
                            print(
                                f"  reading: {inp.get('file_path', '')}",
                                flush=True,
                            )
                        elif tool == "Bash":
                            print(
                                f"  running: {inp.get('command', '')}",
                                flush=True,
                            )
                        elif tool == "Write":
                            print(
                                f"  writing: {inp.get('file_path', '')}",
                                flush=True,
                            )
                        elif tool == "Edit":
                            print(
                                f"  editing: {inp.get('file_path', '')}",
                                flush=True,
                            )
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


def print_output_sections(response_text, response_instructions, config):
    """Print the standard output sections for the main agent."""
    print(f"\n[response]")
    print(response_text.strip())
    print(f"[end response]")

    print(f"\n[response-instructions]")
    print(response_instructions.strip())
    print(f"[end response-instructions]")

    if config.get("reinforce_subagent_rules", True):
        script_path = find_script_path()
        print(f"\n[context-db-sub-agent-usage-reminder]")
        print(generate_brief(config, script_path))
        print(f"[end context-db-sub-agent-usage-reminder]")


# ── Mode runners ───────────────────────────────────────────────────────────


def run_review(args):
    """Run the review subagent from project root — it diffs and checks conventions."""
    context_db = (
        os.path.abspath(args.context_db) if args.context_db != "." else find_context_db()
    )
    if not os.path.isdir(context_db):
        print(f"Error: context-db not found: {context_db}", file=sys.stderr)
        sys.exit(1)

    config = load_config(args.config)
    review_cfg = config["review"]
    model = args.model or review_cfg["model"]
    scope = review_cfg.get("scope", "context-db-only")
    toc = os.path.abspath(args.toc_script or find_toc_script())
    project_root = find_project_root(context_db)
    context_db_rel = os.path.relpath(context_db, project_root)
    debug = args.debug

    system_prompt = build_review_prompt(toc, context_db_rel, scope)
    user_msg = USER_PROMPTS["review"].format(prompt=args.prompt)

    if debug:
        print(f"cwd: {project_root}")
        print(f"context-db: {context_db_rel}/")
        print(f"model: {model}")
        print(f"scope: {scope}")
        print(f"\n[system prompt]\n{system_prompt}\n[end]")
        print(f"\n[user message]\n{user_msg}\n[end]\n")

    text, cost_usd, elapsed = spawn_claude(
        system_prompt, user_msg, model, MODE_TOOLS["review"], project_root, debug
    )

    if text is None:
        sys.exit("Error: review subagent timed out")

    response_instructions = (
        "The review subagent has checked your changes against project "
        "conventions in context-db.\n"
        "IMPORTANT: This review may have been generated by a less capable "
        "model — treat it as advisory. Evaluate each item yourself, fix "
        "real issues, and ignore false positives."
    )

    print_output_sections(text, response_instructions, config)

    if debug:
        print(f"\n[metadata]")
        print(f"model: {model} | cost: ${cost_usd:.4f} | time: {elapsed:.1f}s")


def run_subagent(args):
    """Run a single-phase subagent (ask)."""
    context_db = (
        os.path.abspath(args.context_db) if args.context_db != "." else find_context_db()
    )
    if not os.path.isdir(context_db):
        print(f"Error: context-db not found: {context_db}", file=sys.stderr)
        sys.exit(1)

    config = load_config(args.config)
    model = args.model or config[args.mode]["model"]
    toc = os.path.abspath(args.toc_script or find_toc_script())

    system_prompt = SYSTEM_PROMPTS[args.mode].format(toc=toc)
    user_msg = USER_PROMPTS[args.mode].format(prompt=args.prompt)
    debug = args.debug

    if debug:
        print(f"cwd: {context_db}")
        print(f"model: {model}")
        print(f"\n[system prompt]\n{system_prompt}\n[end]")
        print(f"\n[user message]\n{user_msg}\n[end]\n")

    text, cost_usd, elapsed = spawn_claude(
        system_prompt, user_msg, model, MODE_TOOLS[args.mode], context_db, debug
    )

    if text is None:
        sys.exit("Error: subagent timed out (1h)")

    response_instructions = (
        "The response above comes from a context agent with access to the "
        "project's context-db knowledge base — conventions, design "
        "decisions, gotchas, and standards. The context agent reads the "
        "project's context-db/ folder for you, so you normally do not "
        "need to, but feel free if you think it would be useful.\n"
        "IMPORTANT: This information is a starting point and could be "
        "incomplete or have other issues — you are the final expert and "
        "need to corroborate and double check against other assets in "
        "this project (e.g. the code, docs, READMEs, whatever makes "
        "sense and is relevant) before answering, writing code or docs, "
        "or whatever task is being required. But do follow any project "
        "standards that are returned (if applicable). "
        "REMEMBER: trust but verify!"
    )

    print_output_sections(text, response_instructions, config)

    if debug:
        print(f"\n[metadata]")
        print(f"model: {model} | cost: ${cost_usd:.4f} | time: {elapsed:.1f}s")


def get_context_db_diff(project_root, context_db_rel):
    """Capture git diff and new files for context-db changes.

    Returns (diff_text, has_changes). diff_text includes both modified
    file diffs and full content of new untracked files.
    """
    # Modified/deleted tracked files
    diff_result = subprocess.run(
        ["git", "diff", context_db_rel + "/"],
        capture_output=True,
        text=True,
        cwd=project_root,
    )
    diff_text = diff_result.stdout.strip()

    # New untracked files
    untracked_result = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard", context_db_rel + "/"],
        capture_output=True,
        text=True,
        cwd=project_root,
    )
    untracked = untracked_result.stdout.strip()

    # Build combined diff
    sections = []
    if diff_text:
        sections.append(diff_text)

    if untracked:
        for fpath in untracked.split("\n"):
            fpath = fpath.strip()
            if not fpath:
                continue
            full_path = os.path.join(project_root, fpath)
            if os.path.isfile(full_path):
                with open(full_path) as f:
                    content = f.read()
                lines = content.splitlines()
                pseudo_diff = (
                    f"--- /dev/null\n+++ b/{fpath}\n"
                    f"@@ -0,0 +1,{len(lines)} @@"
                )
                for line in lines:
                    pseudo_diff += f"\n+{line}"
                sections.append(pseudo_diff)

    combined = "\n\n".join(sections)
    return combined, bool(combined)


def run_update_context_db(args):
    """Two-phase update: subagent makes changes, then review subagent checks."""
    context_db = (
        os.path.abspath(args.context_db) if args.context_db != "." else find_context_db()
    )
    if not os.path.isdir(context_db):
        print(f"Error: context-db not found: {context_db}", file=sys.stderr)
        sys.exit(1)

    config = load_config(args.config)
    mode_config = config["update-context-db"]
    model = args.model or mode_config["model"]
    toc = os.path.abspath(args.toc_script or find_toc_script())
    debug = args.debug

    # ── Phase 1: Update ────────────────────────────────────────────────
    system_prompt = SYSTEM_PROMPTS["update-context-db"].format(
        toc=toc, cwd=context_db
    )
    user_msg = USER_PROMPTS["update-context-db"].format(prompt=args.prompt)

    if debug:
        print(f"[phase 1: update]")
        print(f"cwd: {context_db}")
        print(f"model: {model}")
        print(f"\n[system prompt]\n{system_prompt}\n[end]")
        print(f"\n[user message]\n{user_msg}\n[end]\n")

    update_text, update_cost, update_time = spawn_claude(
        system_prompt,
        user_msg,
        model,
        MODE_TOOLS["update-context-db"],
        context_db,
        debug,
    )

    if update_text is None:
        sys.exit("Error: update subagent timed out")

    # ── Check for changes ──────────────────────────────────────────────
    project_root = find_project_root(context_db)
    context_db_rel = os.path.relpath(context_db, project_root)

    diff_text, has_changes = get_context_db_diff(project_root, context_db_rel)

    if not has_changes:
        response_instructions = (
            "The update subagent found nothing to change. This may mean "
            "the knowledge is already captured, or the learnings weren't "
            "specific enough to file."
        )
        print_output_sections(
            f"No changes were made to context-db.\n\n"
            f"Update agent summary:\n{update_text.strip()}",
            response_instructions,
            config,
        )
        if debug:
            print(f"\n[metadata]")
            print(
                f"update: model={model} cost=${update_cost:.4f} time={update_time:.1f}s"
            )
        return

    # ── Phase 2: Review ────────────────────────────────────────────────
    review_cfg = mode_config.get("review", {})
    review_enabled = review_cfg.get("enabled", True)

    if not review_enabled:
        response_instructions = (
            "The update subagent made changes to context-db/. Review is "
            "disabled — verify the changes yourself if needed."
        )
        print_output_sections(
            f"context-db has been updated (review skipped).\n\n"
            f"Update agent summary:\n{update_text.strip()}",
            response_instructions,
            config,
        )
        if debug:
            print(f"\n[metadata]")
            print(
                f"update: model={model} cost=${update_cost:.4f} time={update_time:.1f}s"
            )
        return

    review_model = review_cfg.get("model", "sonnet")
    review_user_msg = (
        f"## Learnings that were filed\n\n{args.prompt}\n\n"
        f"## Git diff of changes\n\n```diff\n{diff_text}\n```"
    )

    if debug:
        print(f"\n[phase 2: review]")
        print(f"model: {review_model}")
        print(f"diff size: {len(diff_text)} chars")

    review_text, review_cost, review_time = spawn_claude(
        REVIEW_UPDATE_PROMPT, review_user_msg, review_model, "Bash,Read",
        project_root, debug,
    )

    if review_text is None:
        review_text = "Review timed out — manual review recommended."
        print("Warning: review subagent timed out", file=sys.stderr)

    response_instructions = (
        "The update subagent made changes to context-db/ and a review "
        "subagent has checked those changes.\n"
        "IMPORTANT: This review may have been generated by a less capable "
        "model — treat it as advisory. Evaluate each item yourself, fix "
        "real issues in context-db, and ignore false positives."
    )
    print_output_sections(
        f"Update agent summary:\n{update_text.strip()}\n\n"
        f"Review:\n{review_text.strip()}",
        response_instructions,
        config,
    )

    if debug:
        print(f"\n[metadata]")
        print(
            f"update: model={model} cost=${update_cost:.4f} time={update_time:.1f}s"
        )
        print(
            f"review: model={review_model} cost=${review_cost:.4f} "
            f"time={review_time:.1f}s"
        )
        total_cost = update_cost + review_cost
        total_time = update_time + review_time
        print(f"total: cost=${total_cost:.4f} time={total_time:.1f}s")


# ── CLI ─────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="context-db subagent")
    parser.add_argument(
        "mode", choices=["instructions", "ask", "review", "update-context-db"]
    )
    parser.add_argument("prompt", nargs="?", default="")
    parser.add_argument("--model", help="Override model")
    parser.add_argument("--context-db", default=".", help="Path to context-db/")
    parser.add_argument("--config", default=".contextdb.json")
    parser.add_argument("--toc-script", help="Path to TOC script")
    parser.add_argument(
        "--brief",
        action="store_true",
        help="Short version of instructions (for reinforcement)",
    )
    parser.add_argument(
        "--ask-when",
        choices=["never", "major", "always"],
        help="Override ask frequency for testing",
    )
    parser.add_argument(
        "--review-when",
        choices=["never", "major", "always"],
        help="Override review frequency for testing",
    )
    parser.add_argument(
        "--update-context-db-when",
        choices=["never", "major", "always"],
        help="Override update-context-db frequency for testing",
    )
    parser.add_argument("--debug", action="store_true")

    args = parser.parse_args()

    if args.mode == "instructions":
        config = load_config(args.config)
        # Apply --*-when overrides for testing
        if args.ask_when:
            config["ask"]["when"] = args.ask_when
        if args.review_when:
            config["review"]["when"] = args.review_when
        if args.update_context_db_when:
            config["update-context-db"]["when"] = args.update_context_db_when
        script_path = find_script_path()
        if args.brief:
            print(generate_brief(config, script_path))
        else:
            print(generate_instructions(config, script_path))
    elif args.mode == "update-context-db":
        if not args.prompt:
            parser.error(f"{args.mode} mode requires a prompt")
        run_update_context_db(args)
    elif args.mode == "review":
        if not args.prompt:
            parser.error(f"{args.mode} mode requires a prompt")
        run_review(args)
    else:
        if not args.prompt:
            parser.error(f"{args.mode} mode requires a prompt")
        run_subagent(args)


if __name__ == "__main__":
    main()
