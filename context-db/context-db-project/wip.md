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

## Sub-agent system overhaul — in progress

Sub-agent architecture rebuilt with composable templates. Three template
directories: `main-agent/` (core, reused), `sub-agent/` (role + constraints),
`spawn/` (dispatch instructions). Config `rerun-init` flag replaces old
`response-*.md` remind templates.

Done:

- `prompt` command — role-prompt.md tested with haiku, working
- Prompt-as-data pattern (`[main-user-prompt]` in system prompt)
- Response wrapping (`[context-usage]` + `[context-db-findings]`)
- Spawn templates for all three commands

Remaining:

- `pre-review` command — needs `role-pre-review.md`
- `review` command — needs `role-review.md`
- Clean up deprecated files (`role.md`, `navigation-constraints.md` — superseded
  by per-command role files)
- Test pre-review and review with haiku
- Delete `old-prompts/` once all commands are verified

## Main-agent skill is working well

The unified `/context-db` skill with sub-commands (`prompt`, `pre-review`,
`review`, `update`, `maintain`) is stable. Python TOC script passes 72/72 tests.
Template-based prompt composition is clean. No known issues.
