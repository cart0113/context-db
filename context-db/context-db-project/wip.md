---
description: Active work items. Update as items are completed or added.
---

# Work in Progress

## Docs site overview is outdated

`docs/src/overview/overview.md` still references bash scripts, old skill names
(`context-db-manual`, `context-db-reindex`, `context-db-maintain`), and the old
multi-skill folder structure. Needs syncing with the updated
`context-db/context-db-project/overview.md` per the convention in
`writing-docs/sync-overview-readme.md`. The overview symlink was broken during
the 2026-04-14 maintain pass — the context-db version is now a standalone file
with frontmatter as it should have been.

## Sub-agent system needs overhaul

`context-db-sub-agent.py` spawns `claude -p` for isolated context-db lookups.
The architecture works but the implementation needs rethinking:

- Prompt engineering from the old subagent era (pre-unify) may not match current
  template structure
- The sub-agent modes (user-prompt, pre-review, code-review) were designed
  around the old multi-skill system — need to verify they still make sense as
  sub-commands of the unified skill
- No real-world testing since the unify refactor
- Lessons from `lessons-learned.md` (cheap model constraints, content-first
  ordering, navigation constraints) need to be verified against current prompts

The sub-agent is not currently invoked by default — main-agent mode handles all
commands. Sub-agent mode is opt-in via config.

## Main-agent skill is working well

The unified `/context-db` skill with sub-commands (`prompt`, `pre-review`,
`review`, `update`, `maintain`) is stable. Python TOC script passes 72/72 tests.
Template-based prompt composition is clean. No known issues.
