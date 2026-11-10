---
type: Reference
description:
  Step-by-step guide for an agent migrating a project's context-db from v0.0 to
  v0.1 (OKF format) — install the new skill, run the migration script,
  configure, fix lint, and handle shared bundles, ON files, and wip. Includes
  the full list of what changed.
---

# Migrating a project from v0.0 to v0.1

Follow these steps in the project being migrated. `<cdb-repo>` is a checkout of
this repository on the `v0.1` branch. Work on a branch and commit at the end.

## What changed

| v0.0                                              | v0.1                                                    |
| ------------------------------------------------- | ------------------------------------------------------- |
| Frontmatter: `description`                        | Frontmatter: `type` and `description` (OKF)             |
| TOC printed by `context-db-generate-toc.py`       | Generated `index.md` in every folder, read directly     |
| Commands `prompt`, `update`, `maintain`, `read`   | Commands `prompt`, `update`, `wip`, `configure`         |
| No config                                         | `context-db/context-db.json` plus optional `.local.json` |
| `context-db/ON_PROMPT.md` at the root             | `context-db/context-db-on-markdown/ON_PROMPT.md`        |
| `ON_MAINTAIN.md`                                  | Gone. `ON_WIP.md` and `ON_CONFIGURE.md` are new         |
| `<name>-project/wip.md`                           | `<name>-project/wip/` folder                            |
| Backticked paths, resolver script for `..`        | Markdown links; a shared bundle links only within itself |
| Six `status` values                               | `draft`, `stable`, `deprecated`                         |
| `_drafts/` folders hidden from the TOC            | No hidden folders; use `wip/`                           |
| Symlinks anywhere                                 | Symlinks only at the top level of `context-db/`         |
| Three scripts under `.claude/skills/context-db/scripts/` | One script, `.claude/skills/context-db/context-db.py` |

## 1. Replace the skill

Remove the old skill and install the new one. Copy it, or symlink it if the
project already symlinked the old one:

```bash
rm -rf .claude/skills/context-db
cp -r <cdb-repo>/skill/context-db .claude/skills/context-db
```

For agents that do not use `.claude/skills/`, put the folder wherever that
agent's skills live. The script finds its prompts relative to itself.

## 2. Run the migration script

```bash
python3 <cdb-repo>/context-db/context-db-project/context-db-migrate-from-v0.0/migrate-v0.0.py context-db --dry-run
python3 <cdb-repo>/context-db/context-db-project/context-db-migrate-from-v0.0/migrate-v0.0.py context-db
```

It adds a guessed `type` to every file, maps retired statuses to `draft`,
converts backticked relative paths to links, and moves the ON files and
`wip.md`. It prints what it changed and a "Needs a decision" list. Keep that
list; steps 4 to 6 work through it.

## 3. Configure

```bash
python3 .claude/skills/context-db/context-db.py init --project <name> --python <command> --main-branch <branch>
```

`<name>` is the existing project folder's name without the `-project` suffix.
Ask the user for `--python` if `python3` is not right for the whole team; for a
path that is right only on their machine add `--local python=<path>` instead.
`init` creates the config, the missing ON files, and `wip/`, then generates
every `index.md` and prints lint.

## 4. Fix lint until clean

Run `python3 .claude/skills/context-db/context-db.py index` after each round.

- **Guessed types.** Review them. The guess is keyword-based and defaults to
  `Reference`. The vocabulary is `Folder`, `Decision`, `Convention`,
  `Architecture`, `Gotcha`, `Reference`, `Research`, `Plan`.
- **No folder descriptor.** Add `<folder>/<folder>.md` with `type: Folder` and a
  description. v0.0 also accepted `<folder>-instructions.md`, `SKILL.md`,
  `CONTEXT.md`, and `AGENTS.md` as descriptors; rename those.
- **No frontmatter.** v0.0 allowed a fenced `yaml description` block instead.
  Convert it to real frontmatter.
- **Broken or root-relative links.** Make them file-relative. A link that left a
  shared bundle through `..` has to go, or the target has to move inside.
- **Oversized files and folders** are warnings. Split them when convenient.

## 5. ON files, drafts, wip

- `ON_MAINTAIN.md`: `maintain` no longer exists. Move anything still wanted into
  `context-db-on-markdown/ON_UPDATE.md`, then delete it.
- `_drafts/` folders are now ordinary folders. Move live plans into
  `<name>-project/wip/` and delete the rest.
- The old `wip.md` is now `wip/current-work.md`. Give it `type: Plan`, delete
  finished items, and split it by effort if it covers several. Running
  `/context-db wip` afterwards does this properly.
- Delete notes that describe the v0.0 machinery itself (the TOC script, the
  resolver, `maintain`).

## 6. Shared bundles

The migration script and `index` both skip symlinked folders. For each one, go
to the repository that owns it and there:

```bash
python3 <cdb-repo>/context-db/context-db-project/context-db-migrate-from-v0.0/migrate-v0.0.py context-db
python3 <cdb-repo>/skill/context-db/context-db.py index context-db/<bundle>
```

Passing the bundle path means that repository needs no config of its own.
Commit there. Until that is done the bundle still works here; `prompt` tells the
agent to list the folder instead of reading an index.

## 7. Standing instructions and hooks

- Replace the context-db section of `AGENTS.md` or `CLAUDE.md` with
  `.claude/skills/context-db/starters/AGENTS.md`. The command list changed.
- If the project has a pre-commit hook or CI, add
  `<python> .claude/skills/context-db/context-db.py index --check`.
- Remove references to the deleted scripts from any project docs or hooks.

## 8. Verify

```bash
python3 .claude/skills/context-db/context-db.py index --check
python3 .claude/skills/context-db/context-db.py prompt "test"
```

The first must exit 0 and call the bundle conformant. The second must list the
project bundle with a real description, every background bundle, and the wip
files. Then commit.

The v0.0 system remains on the `v0.0` branch of this repository.
