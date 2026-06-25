---
description:
  v0.0 refactor — radical simplification to four commands (prompt, update,
  maintain, read), no config, no sub-agent, no startup hooks. The old
  multi-command/sub-agent system lives on the pre-v0.0 branches.
status: stable
---

# v0.0 Refactor

**Branch**: `v0.0` (new default). **Started**: 2026-06-25.

## Why

The unify-era system (see `./unify-refactor.md`) accumulated too many moving
parts to explain: per-command `mode` (`main-agent`/`sub-agent`) and `model`
selection, a `.context-db.json` config file, `on_start` / `on_all` /
`on_<command>` glob tiers, a `claude -p` sub-agent spawner, and a session-start
rule that ran `load-start-context`. The core read/write loop (`prompt`,
`update`, `maintain`) was working great; everything around it added surface area
without pulling its weight. The goal of v0.0: make the core skill front and
center and simple enough that it needs no explanation.

## What changed

**Commands cut to four**, all main-agent, no config:

- `prompt`, `update`, `maintain` — unchanged in spirit.
- `read [folder]` — instructs the agent to read a folder exhaustively (this is
  the old `read-all`; the old content-inlining `read` is gone).
- `help` — alias for `--help`.

**Removed entirely:**

- `pre-review` and `review` commands (and their templates/docs).
- The sub-agent path: `context-db-sub-agent.py`, `prompts/sub-agent/`,
  `prompts/spawn/`, `prompts/old-prompts/`, and all `mode`/`model` selection.
- `.context-db.json` and all config loading.
- `load-start-context`, `load-manual`, and the session-start rule/hook. There is
  no startup behavior anymore — the system is fully opt-in.
- `on_start` / `on_all` / `on_<command>` glob tiers and the docs that described
  them (`configuring-posture`, `rules`, `sub-agents`, `config-effects`).

**Added:**

- Three optional special files at the **root** of `context-db/`: `ON_PROMPT.md`,
  `ON_UPDATE.md`, `ON_MAINTAIN.md`. If present, each is inlined automatically
  when its command runs. Fixed names, no config — presence is the only switch.
  Give them frontmatter so they show in the root TOC; it is stripped on inline.
- `templates/AGENTS.md` — opt-in boilerplate a user pastes into their agent's
  standing-instructions file (`AGENTS.md` / `CLAUDE.md` / `.cursor/rules/` /
  `copilot-instructions.md`) to teach the agent the commands. Nothing fires
  unless the user opts in or invokes a command directly.

## Where the old system lives

The full unify/sub-agent system is preserved on the pre-v0.0 branches — `main`,
`unify`, and `feature-sub-agent`. Nothing was force-pushed or rewritten; to
inspect or revive the old mode/model/sub-agent/config machinery, check out those
branches. v0.0 is a clean break, not a migration — no backward-compat shims for
the old config or commands.

The historical design-decision records under `../design-decisions/` and
`../lessons-learned.md` still reference sub-agent/config concepts. They are kept
as history of how the project got here; a `/context-db maintain` pass can prune
what no longer reflects v0.0.
