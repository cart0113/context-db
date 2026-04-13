---
description:
  Unify refactor — consolidating 5 skills, 2 hooks, 2 rules into a single
  /context-db skill with sub-commands
status: work-in-progress
---

# Unify Refactor

**Started**: 2026-04-12 **Branch**: `unify` (from `feature-sub-agent` at
`d8c0c30`) **Checkpoint**: `feature-sub-agent` at `d8c0c30` is the stable
pre-refactor state.

## Why

Too many moving parts: 5 skills (`context-db-manual`, `context-db-subagent`,
`context-db-reindex`, `context-db-maintain`, `bruha-audit-docs`), 2 hooks, 2
rules, 2 `.claude-project` template variants. Agents don't follow automated
instructions reliably over time (context rot, compression). User-initiated
commands are more reliable than trying to teach agents to auto-fire.

## What

Single skill: `/context-db <command>` with sub-commands:

- `prompt` — consult context-db (READ)
- `pre-review` — check plan against standards (READ)
- `review` — review changes against conventions (READ)
- `update` — file learnings (WRITE)
- `maintain` — 7-phase audit + reindex (WRITE)
- `init` — startup (internal, not in SKILL.md)

Two scripts:

- `context-db-main-agent.py` — dispatcher, always called by SKILL.md
- `context-db-sub-agent.py` — `claude -p` spawner, called when mode=sub-agent

All prompts externalized as `.md` templates in `scripts/prompts/`. Python TOC
script replaces bash.

## Key decisions

- User-initiated, not auto-firing. `init` stubbed for later.
- Re-instruct on every call (handles context rot).
- Mode per command: `sub-agent` | `main-agent` | `ask`.
- Config: JSON with `defaults` section + per-command overrides.
- Consistent hyphenation: `sub-agent`, `main-agent`, `pre-review`.
