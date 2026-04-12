---
description:
  Subagent architecture — script entry point, four modes (user-prompt,
  code-review, update-context-db, instructions), how each mode spawns claude -p,
  tools per mode, review-type config, stream-json output
---

# Subagent Architecture

## Single script, four modes

`context-db-sub-agent.py` is the only script. It handles all four modes:

- **instructions** — reads `.contextdb.json`, outputs tailored directives for
  the main agent. Called by the session-start hook and the rule. The main agent
  never sees `.contextdb.json`.
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

## Config (.contextdb.json)

Per-mode settings at the top level (not nested under "modes"):

```json
{
  "user-prompt": { "model": "haiku", "when": "major" },
  "code-review": {
    "model": "sonnet",
    "when": "major",
    "review-type": "context-db"
  },
  "update-context-db": { "model": "sonnet", "when": "major" }
}
```

- `model`: haiku, sonnet, or opus
- `when`: never, major, always
- `review-type` (code-review only): context-db or full

## Environment guard

The script sets `CONTEXT_DB_SUBAGENT=1` in the environment before calling
`claude -p`. The session-start hook checks this and exits early — prevents the
subagent from receiving its own instructions recursively.
