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

## Progress

- Step 1: Branch + structure — done
- Step 2: Python TOC script — done (72/72 tests, identical to bash)
- Step 3: Prompt templates — done (20 templates extracted)
- Step 4: context-db-main-agent.py — done (dispatcher with mode routing)
- Step 5: context-db-sub-agent.py — done (claude -p spawner, end-to-end tested)
- Step 6: SKILL.md + wiring — done (rule, hook, config, GIT_STANDARDS template)
- Step 7: Testing — done (TOC 72/72, sub-agent end-to-end, dispatcher all modes)
- Step 8: Migration + cleanup — done (old skills/hooks/rules deleted, symlinks
  updated, old context-db docs marked deprecated, GIT_STANDARDS updated)

## Key decisions

- User-initiated, not auto-firing. `init` stubbed for later.
- Re-instruct on every call (handles context rot).
- Two scripts: `context-db-main-agent.py` (dispatcher) and
  `context-db-sub-agent.py` (claude -p spawner).
- Mode per command: `sub-agent` | `main-agent` | `ask`.
- Config: JSON with `defaults` section + per-command overrides.
- `update --commit` flag: after context-db writes, commits all affected files
  with a message distilled from the same learnings. Makes `git log` a parallel
  record of project knowledge alongside context-db.
- Prompts externalized as editable `.md` templates in `scripts/prompts/`.
- Python TOC replaces bash TOC (identical output, 72/72 tests pass).
- Consistent hyphenation: `sub-agent`, `main-agent`, `pre-review`.
