---
name: context-db-subagent
description:
  'Context-db subagent mode — delivers project knowledge via an isolated
  subagent that navigates context-db itself. Load this skill to see how the
  system works or to troubleshoot.'
allowed-tools: Bash Read
---

## How it works

A thin Python wrapper calls `claude -p` with Bash and Read tools. The subagent
model navigates context-db using the same B-tree pattern as the manual skill —
runs the TOC script, reads descriptions, drills into relevant folders, reads
files. The main agent never touches context-db directly.

## The script

One entry point, four modes:

```
python3 .claude/skills/context-db-subagent/scripts/context-db-sub-agent.py <mode> "<prompt>"
```

### Modes

- **instructions** — Read config, return tailored instructions for the main
  agent. Called by the session-start hook and the rule. The main agent never
  needs to see `.contextdb.json`.
- **user-prompt** — Forward the user's raw prompt. The subagent navigates
  context-db and returns verbatim snippets of relevant conventions, standards,
  pitfalls.
- **code-review** — Send a summary of changes. The subagent runs `git diff`,
  checks against project conventions, and returns a review report. Configurable
  via `review-type`: `context-db` (default, sonnet) or `full` (context-db +
  general code review, opus).
- **update-context-db** — Send what you learned. The subagent determines where
  to file it in context-db, then a review subagent checks the changes.

### Config

`.contextdb.json` in the project root controls:

- Which model each mode uses (haiku, sonnet, opus)
- `when` per mode: `always`, `major` (significant new work), `never`
- `review-type` (code-review only): `context-db` or `full`

The main agent never reads this file. The `instructions` mode reads it and
returns the right instructions.

### Manual fallback

If the subagent isn't working or you need direct access to context-db files,
load the `/context-db-manual` skill instead. Same knowledge base, direct file
access.
