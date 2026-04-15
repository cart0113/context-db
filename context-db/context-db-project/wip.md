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

- All three per-command role files: `role-prompt.md`, `role-pre-review.md`,
  `role-review.md`
- Prompt-as-data pattern (`[main-user-prompt]` in system prompt)
- Response wrapping: prefix (`[context-usage]`) + findings + suffix
  (`[interpreting-*-response]`)
- Spawn templates for all three commands
- Review: full review is default, `--context-db-only-review` flag for rare case
- Review: composable instructions (`review-instructions.md` +
  `review-instructions-context-db-only.md`)

Remaining:

- Clean up deprecated files (`role.md`, `navigation-constraints.md`,
  `output-format.md`, `output-format-review.md`, `output-format-review-full.md`
  — superseded by per-command role files and review-instructions)
- Test pre-review with haiku
- Delete `old-prompts/` once all commands are verified
- Consider cleaning up unused output-context-db-review.md and
  output-general-review.md (superseded by review-instructions.md)

## Main-agent skill is working well

The unified `/context-db` skill with sub-commands (`prompt`, `pre-review`,
`review`, `update`, `maintain`) is stable. Python TOC script passes 72/72 tests.
Template-based prompt composition is clean. No known issues.
