---
description:
  Subagent architecture — script entry point, five modes (pre-review,
  user-prompt, code-review, update-context-db, instructions), how each mode
  spawns claude -p, tools per mode, review-type config, uncommitted-changes
  config, combined workflow, stream-json output
---

# Subagent Architecture

## Single script, five modes

`context-db-sub-agent.py` is the only script. It handles all five modes:

- **instructions** — reads `.contextdb.json`, outputs tailored directives for
  the main agent. Called by the session-start hook and the rule. The main agent
  never sees `.contextdb.json`.
- **pre-review** — calls `claude -p` from inside context-db/. The agent sends a
  structured plan (type/language/size) before starting edits; the subagent
  returns verbatim standards snippets that apply. Runs before code-review.
- **user-prompt** — calls `claude -p` from inside context-db/ so the subagent
  navigates the knowledge base and returns relevant context as verbatim
  snippets.
- **code-review** — calls `claude -p` from the project root. The subagent runs
  `git diff` itself, navigates context-db for conventions, and returns a
  human-readable review report on stdout.
- **update-context-db** — calls `claude -p` from the project root. The subagent
  runs `git diff` to see what changed, navigates context-db to understand
  existing knowledge, then writes/edits context-db files directly.

## Execution model per mode

### pre-review — runs from context-db/

- Tools: `Bash,Read`
- The agent (not the user) sends a structured plan before starting edits:
  - `type`: what kind of change (feature, refactor, bugfix, docs, etc.)
  - `language`: programming language(s) involved
  - `size`: rough scope (small, medium, large)
- The subagent navigates context-db for applicable coding/writing standards and
  returns verbatim snippets — not a summary. The agent reads these before
  touching any files.
- Default model: haiku (fast and cheap — the agent is just fetching standards,
  not doing analysis).
- Designed to solve the problem of main agents ignoring standards. Feeding
  standards _before_ the agent starts editing is more reliable than expecting
  the agent to remember them from context loaded earlier in the session.

### user-prompt — runs from context-db/

- Tools: `Bash,Read`
- The subagent navigates the B-tree (TOC script + Read), returns verbatim
  snippets from relevant files.
- Does NOT answer the prompt or help with the task.

### code-review — runs from project root

- Tools: `Bash,Read`
- The subagent runs `git diff` itself to see what changed.
- Navigates context-db (via TOC script with `context-db/` prefix) to find
  relevant conventions.
- Returns a full review report citing context-db sources for each critique.
- **review-type** config controls what gets reviewed:
  - `context-db` (default, sonnet): only flag issues backed by context-db
    conventions. No general opinions.
  - `full` (opus): also do a general code review. Report has two sections:
    "Convention Issues" and "General Code Review".
- Requires a clean git baseline — instructions tell main agent to ensure repo is
  committed before making changes.

### update-context-db — runs from project root

- Tools: `Bash,Read,Write,Edit`
- The subagent runs `git diff` to see what code changed this session.
- Navigates context-db (via TOC script with `context-db/` prefix) to understand
  existing knowledge.
- Uses the developer's notes + the diff to update context-db files directly.
- Only files what the code can't tell you — conventions, corrections, pitfalls,
  design rationale.
- Returns a summary on stdout.

## All subagent output goes to stdout

Every mode returns its results in demarcated sections:

```
[response]
{subagent's response}
[end response]

[response-instructions]
{how the main agent should treat this response}
[end response-instructions]

[context-db-sub-agent-usage-reminder]
{brief with commands for next call}
[end context-db-sub-agent-usage-reminder]
```

No files are written. The main agent reads the response inline.

## Combined workflow in instructions output

When both pre-review and code-review are enabled, the `instructions` mode
outputs a single numbered workflow that combines them. This prevents the agent
from treating them as independent optional calls:

1. Run pre-review → receive applicable standards
2. Make the code changes (following those standards)
3. Run code-review → check against conventions
4. Fix any issues found

If pre-review is disabled, the instructions skip step 1. If code-review is
disabled, they skip steps 3-4. The workflow adapts to the enabled modes so the
main agent always sees a coherent sequence.

## Config (.contextdb.json)

Per-mode settings at the top level (not nested under "modes"):

```json
{
  "pre-review": { "model": "haiku", "when": "major" },
  "user-prompt": { "model": "haiku", "when": "major" },
  "code-review": {
    "model": "sonnet",
    "when": "major",
    "review-type": "context-db"
  },
  "update-context-db": { "model": "sonnet", "when": "major" },
  "uncommitted-changes": "ask-user"
}
```

- `model`: haiku, sonnet, or opus
- `when`: never, major, always
- `review-type` (code-review only): context-db or full
- `uncommitted-changes`: how to handle uncommitted changes before code-review
  - `ask-user` (default): agent asks the developer what to do
  - `auto-commit`: agent commits automatically before running the review

## Environment guard

The script sets `CONTEXT_DB_SUBAGENT=1` in the environment before calling
`claude -p`. The session-start hook checks this and exits early — prevents the
subagent from receiving its own instructions recursively.
