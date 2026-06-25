---
description: Active work items. Update as items are completed or added.
---

# Work in Progress

## v0.0 simplification — done (2026-06-25)

Radical cut to four commands (`prompt`, `update`, `maintain`, `read`) plus
`help`. Removed `pre-review`/`review`, the sub-agent path, `.context-db.json`
and all config, `load-start-context`/`load-manual`, the session-start rule/hook,
and the `on_start`/`on_all`/`on_<command>` tiers. Always-on content is now three
optional root files — `context-db/ON_PROMPT.md`, `ON_UPDATE.md`,
`ON_MAINTAIN.md` — inlined automatically when their command runs. Opt-in via
`templates/AGENTS.md`; no startup behavior. Full write-up in
`./refactors/v0-refactor.md`. The old system lives on the `main`, `unify`, and
`feature-sub-agent` branches.

## Follow-ups

- A `/context-db maintain` pass should prune sub-agent/config references that
  survive in `lessons-learned.md` and `design-decisions/` — they are accurate
  history but no longer describe how v0.0 works.
