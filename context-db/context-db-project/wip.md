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

- Per-command instruction files: `prompt-sub-agent-role.md`,
  `pre-review-instructions.md`, `review-instructions.md`,
  `review-instructions-context-db-only.md`
- `# Main Prompt` / `# User Guidance` — conditional injection when user provides
  a prompt, with `{user_guidance_note}` template variable for instructions to
  heed it
- Response wrapping: prefix (`# Context Usage`) + findings + suffix
  (`# Interpreting * Response`)
- Spawn templates for all three commands
- Pre-review: main-agent mode needs no prompt (agent knows plan from
  conversation). Sub-agent mode: spawn template walks agent through writing a
  detailed plan.
- Review: full review is default, `--context-db-only-review` for rare case

Remaining:

- Clean up deprecated files (`role.md`, `role-review.md`, `role-pre-review.md`,
  `navigation-constraints.md`, `output-format.md`, `output-format-review.md`,
  `output-format-review-full.md`, `output-context-db-review.md`,
  `output-general-review.md`)
- Test pre-review with haiku
- Delete `old-prompts/` once all commands are verified

## Startup context delivery — resolved

Replaced hook-based `load-manual` compositing with 4 static rule files
(`templates/rules/startup-*.md`). Rules survive compaction, require no config.
Sub-agent integration is handled by the rules themselves — they tell the agent
to call `/context-db prompt`, `/context-db pre-review`, etc., and the mode
config determines whether those run as sub-agents. `load-manual` simplified to
single-section loader for mid-conversation use.

## Main-agent skill is working well

The unified `/context-db` skill with sub-commands (`prompt`, `pre-review`,
`review`, `update`, `maintain`) is stable. Python TOC script passes 72/72 tests.
Template-based prompt composition is clean. No known issues.
