---
description:
  Subagent architecture — script entry point, four modes (ask, review,
  update-context-db, instructions), how each mode spawns claude -p, tools per
  mode, review scope config, stream-json output
---

# Subagent Architecture

## Single script, four modes

`context-db-sub-agent.py` is the only script. It handles all four modes:

- **instructions** — reads `.contextdb.json`, outputs tailored directives for
  the main agent. Called by the session-start hook and the rule. The main agent
  never sees `.contextdb.json`.
- **ask** — calls `claude -p` from inside context-db/ so the subagent navigates
  the knowledge base and returns relevant context.
- **review** — calls `claude -p` from the project root. The subagent runs
  `git diff` itself, navigates context-db for conventions, and returns a
  human-readable review report on stdout.
- **update-context-db** — two-phase: first subagent writes to context-db/
  directly, then a review subagent checks the changes via `git diff`.

## Execution model per mode

### ask — runs from context-db/

- Tools: `Bash,Read`
- The subagent navigates the B-tree (TOC script + Read), returns verbatim
  snippets from relevant files.
- Does NOT answer the prompt or help with the task.

### review — runs from project root

- Tools: `Bash,Read`
- The subagent runs `git diff` itself to see what changed.
- Navigates context-db (via TOC script with `context-db/` prefix) to find
  relevant conventions.
- Returns a full review report citing context-db sources for each critique.
- **Scope config** controls what gets reviewed:
  - `context-db-only` (default): only flag issues backed by context-db
    conventions. No general opinions.
  - `context-db-and-general`: also do a general code review. Report has two
    sections: "Convention Issues" and "General Code Review".
- Requires a clean git baseline — instructions tell main agent to ensure repo is
  committed before making changes.

### update-context-db — two phases

Phase 1 (update): runs from context-db/

- Tools: `Bash,Read,Write,Edit`
- Navigates context-db, then edits/creates files directly.

Phase 2 (review): runs from project root

- Tools: `Bash,Read`
- Script captures `git diff context-db/` (including new untracked files).
- Diff is passed to the review subagent in the user message.
- Checks accuracy, redundancy, structure, value, completeness.

Both phases return on stdout — no report files.

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
  "ask": { "model": "haiku", "when": "major" },
  "review": { "model": "sonnet", "when": "major", "scope": "context-db-only" },
  "update-context-db": {
    "model": "sonnet",
    "when": "major",
    "review": { "enabled": true, "model": "sonnet" }
  }
}
```

- `model`: haiku, sonnet, or opus
- `when`: never, major, always
- `scope` (review only): context-db-only or context-db-and-general
- `review` (update-context-db only): sub-config for the review phase

## Environment guard

The script sets `CONTEXT_DB_SUBAGENT=1` in the environment before calling
`claude -p`. The session-start hook checks this and exits early — prevents the
subagent from receiving its own instructions recursively.
