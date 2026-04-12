#!/usr/bin/env python3
"""
context-db-sub-agent.py — project knowledge subagent.

Calls claude -p from the project root so the model navigates the B-tree
in context-db/ using the TOC script and Read tool. The main agent's context
window stays clean.

Modes:
  instructions       Print directives for the main agent (from .contextdb.json)
  user-prompt        What should the developer know before starting this work?
  pre-review         Given a plan, what standards and conventions apply?
  code-review        Do the changes violate any project conventions?
  update-context-db  File learnings into context-db

Usage:
  context-db-sub-agent.py instructions
  context-db-sub-agent.py instructions --brief
  context-db-sub-agent.py user-prompt "user prompt"
  context-db-sub-agent.py pre-review "Type: code (Python). Size: medium. Plan: ..."
  context-db-sub-agent.py code-review "summary of changes" --debug
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

MODES = ["user-prompt", "pre-review", "code-review", "update-context-db"]

DEFAULT_CONFIG = {
    "user-prompt": {"model": "haiku", "when": "major"},
    "pre-review": {"model": "haiku", "when": "never"},
    # review-type: "context-db" = only flag issues backed by context-db conventions
    #              "full"       = also do a general review
    "code-review": {"model": "sonnet", "when": "never", "review-type": "context-db"},
    "update-context-db": {"model": "sonnet", "when": "never"},
    # "auto-commit" = commit before changes automatically
    # "ask-user"    = ask the user what to do with uncommitted changes
    "uncommitted-changes": "ask-user",
    "reinforce_subagent_rules": True,
}

# Tools granted to each mode's subagent
MODE_TOOLS = {
    "user-prompt": "Bash,Read",
    "pre-review": "Bash,Read",
    "code-review": "Bash,Read",
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
                config[mode].update(user[mode])
        for key in ("uncommitted-changes", "reinforce_subagent_rules"):
            if key in user:
                config[key] = user[key]
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
    return os.path.dirname(context_db)


# ── Instructions mode ───────────────────────────────────────────────────────
# generate_instructions() and generate_brief() produce text that the MAIN AGENT
# sees. This is how the main agent learns when/how to call this script.
# Output goes to stdout via the session-start hook → main agent reads it.
#
# The *_WHEN dicts control the "When:" line in the main agent's instructions.
# The *_BRIEF dicts produce the short reminder appended to every sub-agent response.


# FOR MAIN AGENT: "When should I call this mode?"
# Appears in the session-start instructions under each mode's ## heading.
USER_PROMPT_WHEN = {
    "always": "Run this on every new user prompt. Do not skip it, do not ask.",
    "major": """\
Run this when the user's prompt introduces significant new work or the topic
has changed (e.g. was writing code, now asked to write docs or commit). Skip
follow-ups, small refinements, and clarifications on the same topic.""",
}
PRE_REVIEW_WHEN = {
    "always": "Run this before every change. Do not skip it, do not ask.",
    "major": """\
Run this before significant changes — new features, API changes, new files,
architectural decisions, major doc updates. Skip single-line fixes, renames,
formatting, and changes you are confident about from a prior user-prompt.""",
}
CODE_REVIEW_WHEN = {
    "always": "Run this after every change. Do not skip it, do not ask.",
    "major": """\
Run this after significant edits to files in the project — new features, API
changes, new files, architectural decisions, major doc updates. Skip small
fixes, renames, formatting, and changes you are confident about from a prior
user-prompt, especially if they are follow-on edits to a major edit.""",
}
UPDATE_WHEN = {
    "always": "Run this after every completed task. Do not skip it, do not ask.",
    "major": """\
Run this when important information came up during the session that future
agents should know — user corrections, discovered conventions, surprising
pitfalls. Skip routine work where nothing new was learned.""",
}

# FOR MAIN AGENT: short one-liners for the reminder block appended to every
# sub-agent response. Keeps the main agent aware of the workflow late in session.
USER_PROMPT_BRIEF = {
    "always": "on every new user prompt",
    "major": "when work changes topic or scope (skip follow-ups and small refinements)",
}
PRE_REVIEW_BRIEF = {
    "always": "before every change",
    "major": "before significant changes (skip small fixes, renames, formatting)",
}
CODE_REVIEW_BRIEF = {
    "always": "after every change",
    "major": "after significant changes (skip small fixes, renames, formatting)",
}
UPDATE_BRIEF = {
    "always": "after every completed task",
    "major": "when you learned something future agents should know (skip routine work)",
}


def generate_instructions(config, script_path):
    """Generate directives for the main agent."""
    blocks = [
        "This project has a context sub-agent. You MUST follow the instructions "
        "below."
    ]

    # user-prompt
    when = config["user-prompt"]["when"]
    if when != "never":
        blocks.append(
            f"## user-prompt — before starting work\n\n"
            f"When: {USER_PROMPT_WHEN[when]}\n\n"
            f"Run (timeout 120000ms):\n"
            f"  python3 {script_path} user-prompt \"<the user's exact prompt>\"\n\n"
            f"Wait for the response before taking other actions."
        )

    # Change workflow — pre-review, code-review, or both
    pre_when = config["pre-review"]["when"]
    cr_when = config["code-review"]["when"]
    has_pre = pre_when != "never"
    has_cr = cr_when != "never"

    if has_pre or has_cr:
        uncommitted = config["uncommitted-changes"]
        if uncommitted == "auto-commit":
            uncommitted_instruction = """\
If the repo has uncommitted changes, commit them now to establish a clean
baseline."""
        else:
            uncommitted_instruction = """\
If the repo has uncommitted changes, ask the user whether they'd like you
to commit or if they will, to get a clean baseline."""

        workflow = f"## Making changes — workflow\n\n"

        pre_review_block = f"""\
**Pre-review.** Run:
     python3 {script_path} pre-review "<your plan>"
   Your plan MUST include:
   - Type of changes (code, documentation, config, etc.)
   - Language or system (Python, JavaScript, etc.)
   - Size: minor, medium, major, or total overhaul
   - What you plan to change and why

   Wait for the response. It will return applicable standards \
and conventions. Follow them."""

        has_update = config["update-context-db"]["when"] != "never"

        if has_pre and has_cr:
            step = 1
            workflow += (
                f"When to follow this workflow: "
                f"{PRE_REVIEW_WHEN[pre_when]}\n\n"
                f"{step}. **Baseline.** {uncommitted_instruction}\n\n"
            )
            step += 1
            workflow += (
                f"{step}. **Plan your changes.** Before editing, describe "
                f"what you intend to do.\n\n"
            )
            step += 1
            workflow += f"{step}. {pre_review_block}\n\n"
            step += 1
            workflow += (
                f"{step}. **Make your changes** following the standards "
                f"returned.\n\n"
            )
            step += 1
            workflow += (
                f"{step}. **Code-review.** Run:\n"
                f"     python3 {script_path} code-review "
                f"\"<summary of changes made>\"\n"
                f"   Evaluate each item — treat as advisory, fix real issues, "
                f"ignore false positives."
            )
            if has_update:
                step += 1
                workflow += (
                    f"\n\n{step}. **Update context-db** if you learned "
                    f"something important (see below)."
                )
        elif has_pre:
            workflow += (
                f"When to follow this workflow: "
                f"{PRE_REVIEW_WHEN[pre_when]}\n\n"
                f"1. **Plan your changes.** Before editing, describe what you "
                f"intend to do.\n\n"
                f"2. {pre_review_block}\n\n"
                f"3. **Make your changes** following the standards returned."
            )
        else:
            workflow += (
                f"When to follow this workflow: "
                f"{CODE_REVIEW_WHEN[cr_when]}\n\n"
                f"1. **Baseline.** {uncommitted_instruction}\n\n"
                f"2. **Make your changes.**\n\n"
                f"3. **Code-review.** Run:\n"
                f"     python3 {script_path} code-review "
                f"\"<summary of changes made>\"\n"
                f"   Evaluate each item — treat as advisory, fix real issues, "
                f"ignore false positives."
            )

        blocks.append(workflow)

    # update-context-db
    when = config["update-context-db"]["when"]
    if when != "never":
        blocks.append(
            f"## update-context-db — after completing work\n\n"
            f"When: {UPDATE_WHEN[when]}\n\n"
            f"Before running:\n"
            f"  Commit any pending changes so the subagent can see the "
            f"git diff.\n\n"
            f"Run:\n"
            f"  python3 {script_path} update-context-db "
            f"\"<what you learned>\"\n\n"
            f"Send detailed notes on things learned that cannot be known "
            f"by reading the project assets alone — user corrections, "
            f"discovered conventions, surprising pitfalls. The subagent "
            f"will also consult git diff to understand what changed."
        )

    # How to handle responses
    response_rules = []
    if config["user-prompt"]["when"] != "never":
        response_rules.append("""\
When the user-prompt response comes back: this is a starting point, not a
final answer. Trust but verify — corroborate key claims against the actual
code, docs, or other project assets before answering. Follow any project
standards it returns.""")
    if has_pre:
        response_rules.append("""\
When the pre-review response comes back: these are the standards that apply
to your planned changes. Follow them when making your edits.""")
    if has_cr:
        response_rules.append("""\
When the code-review response comes back: this is feedback for your
consideration, not an order. Verify it makes sense, fix real issues, and
use your judgment.""")
    if response_rules:
        blocks.append(
            "## How to handle responses\n\n" + "\n".join(response_rules)
        )

    blocks.append("If the script fails, tell the user and stop working.")
    return "\n\n".join(blocks)


def generate_brief(config, script_path):
    """Self-contained reminder with commands."""
    lines = ["context-db-sub-agent reminder:"]

    when = config["user-prompt"]["when"]
    if when != "never":
        lines.append("")
        lines.append(f"user-prompt — {USER_PROMPT_BRIEF[when]}:")
        lines.append(f"  python3 {script_path} user-prompt \"<prompt>\"")

    pre_when = config["pre-review"]["when"]
    cr_when = config["code-review"]["when"]

    if pre_when != "never" or cr_when != "never":
        lines.append("")
        lines.append("making changes workflow:")
        step = 1

        if cr_when != "never":
            lines.append(f"  {step}. Ensure repo is committed (clean baseline)")
            step += 1

        if pre_when != "never":
            lines.append(
                f"  {step}. python3 {script_path} pre-review "
                f"\"Type: ... Size: ... Plan: ...\""
            )
            lines.append(f"     Follow returned standards")
            step += 1

        lines.append(f"  {step}. Make changes")
        step += 1

        if cr_when != "never":
            lines.append(
                f"  {step}. python3 {script_path} code-review "
                f"\"<summary of changes>\""
            )
            lines.append(f"     Evaluate response (advisory), fix real issues")

    when = config["update-context-db"]["when"]
    if when != "never":
        lines.append("")
        lines.append(f"update-context-db — {UPDATE_BRIEF[when]}:")
        lines.append(f"  1. Commit pending changes first")
        lines.append(
            f"  2. python3 {script_path} update-context-db \"<learnings>\""
        )

    return "\n".join(lines)


# ── System prompts ──────────────────────────────────────────────────────────
# FOR SUB-AGENTS: these are the --system-prompt passed to `claude -p`.
# The sub-agent sees ONLY this + the user message. No rules, no skills, no CLAUDE.md.
# Placeholders use {toc}, {context_db_rel} — filled via .format() at call time.

SYSTEM_PROMPTS = {
    # All modes run from project root (cwd=project root).
    # user-prompt & pre-review navigate {context_db_rel}/ for knowledge.
    # code-review & update-context-db also run git commands from project root.

    "user-prompt": """\
You are a project knowledge and standards lookup service.

The project knowledge base is at {context_db_rel}/. It is a B-tree of markdown
files (~100 lines each). Navigate it using ONLY these steps:
1. Run: bash {toc} {context_db_rel}/
   This lists subfolders and files with descriptions from their YAML frontmatter.
2. Pick what's relevant to the developer's prompt.
   - If it's a folder, run: bash {toc} {context_db_rel}/<subfolder>/
   - If it's a file, read the whole file.
3. Repeat until you've found what applies.

Do not use find, grep, or ls. Only the TOC script and Read.
The TOC script is an external tool — never read files from its directory.
Never write code. Never answer the prompt. Never help with the task.

Your job: find ALL relevant knowledge from this knowledge base. This includes:
- Background context: pitfalls, gotchas, design decisions, cross-file
  connections, conventions specific to the areas being asked about
- Applicable standards and procedures: based on what the prompt is about,
  look for standards that apply. For example:
  - Coding question → project coding standards, language-specific standards
  - Documentation or writing → writing standards
  - Commit or release → commit procedures, release standards
  - Any other work → whatever standards, procedures, or protocols apply
  Read the prompt and use judgment about what to look for.

Return your findings as a list of verbatim snippets. For each relevant section:
1. One line explaining why this snippet is relevant.
2. The exact text from the file, wrapped in markers:

[{context_db_rel}/path/to/file.md:START-END]
exact file content, copied verbatim
[end]

Do not summarize or paraphrase file content. Quote it exactly.
If nothing is relevant, respond: No relevant project context.""",

    "pre-review": """\
You are a project knowledge and standards lookup service.

A developer is about to make changes. They will tell you:
- What type of changes (code, documentation, config, etc.)
- What language or system (Python, JavaScript, markdown docs, etc.)
- The size (minor, medium, major, total overhaul)
- Their plan for what to change

Your job: find ALL relevant knowledge from this knowledge base. This includes:
- Background context: pitfalls, gotchas, design decisions, cross-file
  connections, conventions specific to the areas being changed
- Applicable standards: general coding standards, language-specific standards,
  writing standards (if documentation), any other rules that apply

Return everything relevant. Be thorough — the developer will use what you
return and won't see what you don't return.

The project knowledge base is at {context_db_rel}/. It is a B-tree of markdown
files (~100 lines each). Navigate it using ONLY these steps:
1. Run: bash {toc} {context_db_rel}/
   This lists subfolders and files with descriptions from their YAML frontmatter.
2. Pick what's relevant to the planned changes.
   - If it's a folder, run: bash {toc} {context_db_rel}/<subfolder>/
   - If it's a file, read the whole file.
3. Repeat until you've covered all applicable areas.

Do not use find, grep, or ls. Only the TOC script and Read.
The TOC script is an external tool — never read files from its directory.
Never write code. Never help with the task. Only return knowledge.

Return your findings as a list of verbatim snippets. For each relevant section:
1. One line explaining why this is relevant to the planned changes.
2. The exact text from the file, wrapped in markers:

[{context_db_rel}/path/to/file.md:START-END]
exact file content, copied verbatim
[end]

Do not summarize or paraphrase. Quote exactly. Err on the side of including
too much rather than too little.
If nothing is relevant, respond: No relevant project context.""",

    # code-review prompt is built dynamically by build_review_prompt()
    "code-review": None,

    "update-context-db": """\
You are maintaining a project knowledge base at {context_db_rel}/.
Your working directory is the project root.

## Step 1: Understand what changed

Run: git diff
to see what changes were made this session.

## Step 2: Navigate existing knowledge

Browse the knowledge base:
  Run: bash {toc} {context_db_rel}/
  Drill into folders: bash {toc} {context_db_rel}/<subfolder>/
  Read files to understand what's already documented.

## Step 3: Update the knowledge base

Using the developer's notes AND the git diff, update {context_db_rel}/:
- Edit existing files when they cover the topic.
- Create new files only for genuinely new topics.
- Use absolute paths for all file operations.

## What belongs in context-db

Only file what the code can't tell you. Ask: "Would removing this cause the
next agent to make a mistake, even after reading the code?" If not, skip it.

Good content: conventions, corrections from the user, pitfalls (ripple effects,
files that must change together but aren't linked by imports), design rationale
invisible in the code, domain knowledge specific to this project.

Bad content: code summaries, what exists, how it's structured, step-by-step
instructions, anything derivable in 30 seconds with ls/grep/read.

## File format

- Every .md file needs YAML frontmatter with `description` field.
- Descriptions are routing decisions — be specific, not vague.
- Target 50-150 lines per file, 200 max.
- 5-10 items per folder.
- Subfolders need a folder descriptor file (<folder-name>.md, frontmatter only).

When done, summarize what you changed and why.""",
}

# FOR SUB-AGENTS: the user message sent to `claude -p` (stdin).
# {prompt} is filled with the main agent's prompt at call time via .format().
USER_PROMPTS = {
    "user-prompt": """\
Find ALL relevant project knowledge for this developer prompt — context,
pitfalls, conventions, and any applicable standards or procedures:

"{prompt}" """,

    "pre-review": """\
Find ALL relevant project knowledge for these planned changes — context,
pitfalls, conventions, and applicable standards:

"{prompt}" """,

    "code-review": """\
Review these changes against project conventions:

"{prompt}" """,

    "update-context-db": """\
File these learnings:

"{prompt}" """,
}


def build_review_prompt(toc, context_db_rel, review_type):
    """FOR SUB-AGENT: build the code-review system prompt.
    Dynamic because review-type adds/removes the general review section."""
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

    if review_type == "full":
        base += """

After the convention review, also perform a general review of the changes using
your own expertise. Flag anything that looks wrong, risky, or could be improved
— regardless of whether it appears in the knowledge base.

Clearly separate the two sections in your report:
  ## Convention Issues (from context-db)
  ## General Review"""
    else:
        base += """

Only flag issues supported by conventions in the knowledge base. Do not add
general code review opinions — if it's not in context-db, don't flag it."""

    base += """

Never suggest fixes — only identify problems."""
    return base


# ── Subagent execution ─────────────────────────────────────────────────────


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

    if config["reinforce_subagent_rules"]:
        script_path = find_script_path()
        print(f"\n[context-db-sub-agent-usage-reminder]")
        print(generate_brief(config, script_path))
        print(f"[end context-db-sub-agent-usage-reminder]")


# ── Response instructions ──────────────────────────────────────────────────
# FOR MAIN AGENT: printed inside [response-instructions] after every sub-agent
# call. Tells the main agent how to treat the response it just received.

RESPONSE_INSTRUCTIONS = {
    "user-prompt": """\
Context and applicable standards from the project's knowledge base. This is
a starting point — corroborate against the actual code and docs before acting.
Follow any project standards returned.""",

    "pre-review": """\
The pre-review subagent has returned project context and applicable standards
for your planned changes — pitfalls, conventions, coding standards, and other
relevant knowledge. These are verbatim quotes from the project's knowledge
base. This response may have been generated by a less capable model — treat
it as additional context. Evaluate each item and use your own judgment on
what applies.""",

    "code-review": """\
The code-review subagent has checked your changes against project conventions
in context-db. This response may have been generated by a less capable
model — treat it as additional insight, not as authoritative. Evaluate each
item yourself, fix real issues, and ignore false positives.""",

    "update-context-db": """\
The update subagent has made changes to context-db/. Review the changes it
reports — verify they look correct and follow context-db conventions.""",
}


# ── Mode runners ───────────────────────────────────────────────────────────


def run_code_review(args):
    """Run the code-review subagent from project root."""
    context_db = (
        os.path.abspath(args.context_db) if args.context_db != "." else find_context_db()
    )
    if not os.path.isdir(context_db):
        print(f"Error: context-db not found: {context_db}", file=sys.stderr)
        sys.exit(1)

    config = load_config(args.config)
    review_cfg = config["code-review"]
    model = args.model or review_cfg["model"]
    review_type = review_cfg["review-type"]
    if review_type == "full" and not args.model:
        model = "opus"
    toc = os.path.abspath(args.toc_script or find_toc_script())
    project_root = find_project_root(context_db)
    context_db_rel = os.path.relpath(context_db, project_root)
    debug = args.debug

    system_prompt = build_review_prompt(toc, context_db_rel, review_type)
    user_msg = USER_PROMPTS["code-review"].format(prompt=args.prompt)

    if debug:
        print(f"cwd: {project_root}")
        print(f"context-db: {context_db_rel}/")
        print(f"model: {model}")
        print(f"review-type: {review_type}")
        print(f"\n[system prompt]\n{system_prompt}\n[end]")
        print(f"\n[user message]\n{user_msg}\n[end]\n")

    text, cost_usd, elapsed = spawn_claude(
        system_prompt, user_msg, model, MODE_TOOLS["code-review"],
        project_root, debug,
    )

    if text is None:
        sys.exit("Error: code-review subagent timed out")

    print_output_sections(text, RESPONSE_INSTRUCTIONS["code-review"], config)

    if debug:
        print(f"\n[metadata]")
        print(f"model: {model} | review-type: {review_type} | cost: ${cost_usd:.4f} | time: {elapsed:.1f}s")


def run_subagent(args):
    """Run a single-phase subagent (user-prompt or pre-review) from project root."""
    context_db = (
        os.path.abspath(args.context_db) if args.context_db != "." else find_context_db()
    )
    if not os.path.isdir(context_db):
        print(f"Error: context-db not found: {context_db}", file=sys.stderr)
        sys.exit(1)

    config = load_config(args.config)
    model = args.model or config[args.mode]["model"]
    toc = os.path.abspath(args.toc_script or find_toc_script())
    project_root = find_project_root(context_db)
    context_db_rel = os.path.relpath(context_db, project_root)
    debug = args.debug

    system_prompt = SYSTEM_PROMPTS[args.mode].format(
        toc=toc, context_db_rel=context_db_rel
    )
    user_msg = USER_PROMPTS[args.mode].format(prompt=args.prompt)

    if debug:
        print(f"cwd: {project_root}")
        print(f"context-db: {context_db_rel}/")
        print(f"model: {model}")
        print(f"\n[system prompt]\n{system_prompt}\n[end]")
        print(f"\n[user message]\n{user_msg}\n[end]\n")

    text, cost_usd, elapsed = spawn_claude(
        system_prompt, user_msg, model, MODE_TOOLS[args.mode], project_root, debug
    )

    if text is None:
        sys.exit("Error: subagent timed out (1h)")

    print_output_sections(text, RESPONSE_INSTRUCTIONS[args.mode], config)

    if debug:
        print(f"\n[metadata]")
        print(f"model: {model} | cost: ${cost_usd:.4f} | time: {elapsed:.1f}s")


def run_update_context_db(args):
    """Single-phase update: subagent gets notes + git diff, makes changes."""
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
    project_root = find_project_root(context_db)
    context_db_rel = os.path.relpath(context_db, project_root)
    debug = args.debug

    system_prompt = SYSTEM_PROMPTS["update-context-db"].format(
        toc=toc, context_db_rel=context_db_rel
    )
    user_msg = USER_PROMPTS["update-context-db"].format(prompt=args.prompt)

    if debug:
        print(f"cwd: {project_root}")
        print(f"context-db: {context_db_rel}/")
        print(f"model: {model}")
        print(f"\n[system prompt]\n{system_prompt}\n[end]")
        print(f"\n[user message]\n{user_msg}\n[end]\n")

    text, cost_usd, elapsed = spawn_claude(
        system_prompt,
        user_msg,
        model,
        MODE_TOOLS["update-context-db"],
        project_root,
        debug,
    )

    if text is None:
        sys.exit("Error: update subagent timed out")

    print_output_sections(text, RESPONSE_INSTRUCTIONS["update-context-db"], config)

    if debug:
        print(f"\n[metadata]")
        print(f"model: {model} | cost: ${cost_usd:.4f} | time: {elapsed:.1f}s")


# ── CLI ─────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="context-db subagent")
    parser.add_argument(
        "mode",
        choices=[
            "instructions", "user-prompt", "pre-review",
            "code-review", "update-context-db",
        ],
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
        "--user-prompt-when",
        choices=["never", "major", "always"],
    )
    parser.add_argument(
        "--pre-review-when",
        choices=["never", "major", "always"],
    )
    parser.add_argument(
        "--code-review-when",
        choices=["never", "major", "always"],
    )
    parser.add_argument(
        "--update-context-db-when",
        choices=["never", "major", "always"],
    )
    parser.add_argument("--debug", action="store_true")

    args = parser.parse_args()

    if args.mode == "instructions":
        config = load_config(args.config)
        if args.user_prompt_when:
            config["user-prompt"]["when"] = args.user_prompt_when
        if args.pre_review_when:
            config["pre-review"]["when"] = args.pre_review_when
        if args.code_review_when:
            config["code-review"]["when"] = args.code_review_when
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
    elif args.mode == "code-review":
        if not args.prompt:
            parser.error(f"{args.mode} mode requires a prompt")
        run_code_review(args)
    else:
        if not args.prompt:
            parser.error(f"{args.mode} mode requires a prompt")
        run_subagent(args)


if __name__ == "__main__":
    main()
