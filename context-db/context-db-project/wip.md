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

## Load-manual sub-agent integration — low priority

load-manual currently only loads main-agent templates. No mechanism for a
startup hook or CLAUDE.md rule to configure load-manual to spawn a sub-agent for
context delivery. The main use case right now is on-demand mode (agent knows
context-db exists, user explicitly invokes `/context-db` commands).

If a use case emerges where auto-loaded sessions need sub-agent context
delivery, load-manual would need to support spawn templates and mode
configuration. Not needed yet — the user controls things manually via
`/context-db <sub-command>`.

## Main-agent skill is working well

The unified `/context-db` skill with sub-commands (`prompt`, `pre-review`,
`review`, `update`, `maintain`) is stable. Python TOC script passes 72/72 tests.
Template-based prompt composition is clean. No known issues.
