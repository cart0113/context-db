---
type: Reference
description:
  Step-by-step guide for an agent migrating a project's context-db from v0.0 to
  v0.1 (Open Knowledge Format) — install the new skill, run the migration
  script, configure, clear out what is obsolete, fix what the checker reports,
  and handle shared folders. Includes the full list of what changed.
---

# Migrating a project from v0.0 to v0.1

Follow these steps in the project being migrated. `<cdb-repo>` is a checkout of
this repository on the `v0.1` branch; the old system is on its `v0.0` branch. Do
the work on a new branch of the project and commit at the end. Ask the user
before deleting anything that is not plainly obsolete.

## What changed

| v0.0                                                     | v0.1                                                     |
| -------------------------------------------------------- | -------------------------------------------------------- |
| Frontmatter: `description`                               | Frontmatter: `type` and `description` (OKF)              |
| TOC printed by `context-db-generate-toc.py`              | TOC printed on demand by `context-db.py toc`, as before  |
| Commands `prompt`, `update`, `maintain`, `read`          | `prompt`, `update`, `wip`, `configure`, `maintain`       |
| No config                                                | `context-db/configuration/settings.md` (+ `.local.md`)   |
| `context-db/ON_PROMPT.md` at the root                    | `context-db/configuration/ON_PROMPT.md`                  |
| `ON_MAINTAIN.md` at the root                             | In `configuration/`; `ON_WIP.md`, `ON_CONFIGURE.md` new  |
| `<name>-project/wip.md`                                  | Optional `<name>-project/wip/`; `wip/wip.md` is the list |
| Backticked paths, resolver script for `..`               | Markdown links; a shared folder links only within itself |
| Six `status` values                                      | `draft`, `stable`, `deprecated`                          |
| `_drafts/` folders hidden from the TOC                   | No hidden folders; use `wip/`                            |
| `<folder>-instructions.md` or `SKILL.md` as a descriptor | Only `<folder>/<folder>.md`                              |
| Symlinks anywhere                                        | Symlinks only at the top level of `context-db/`          |
| Three scripts under `.claude/skills/context-db/scripts/` | One script, `.claude/skills/context-db/context-db.py`    |

## 1. Replace the skill

Look at what is there first:

```bash
ls -ld .claude/skills/context-db
```

If it is a symlink, replace it with a symlink to the new skill:

```bash
ln -sfn <cdb-repo>/skill/context-db .claude/skills/context-db
```

If it is a directory, replace it with a copy:

```bash
rm -rf .claude/skills/context-db
cp -r <cdb-repo>/skill/context-db .claude/skills/context-db
```

For an agent that does not use `.claude/skills/`, put the folder wherever that
agent's skills live. Note which commit you installed, for the commit message:

```bash
git -C <cdb-repo> rev-parse --short HEAD
```

Then read `.claude/skills/context-db/prompts/format.md`. It is the format every
note has to follow, and it defines the `type` values. The steps below assume you
have read it.

## 2. Run the migration script

```bash
python3 <cdb-repo>/context-db/context-db-project/context-db-migrate-from-v0.0/migrate-v0.0.py context-db --dry-run
python3 <cdb-repo>/context-db/context-db-project/context-db-migrate-from-v0.0/migrate-v0.0.py context-db
```

It adds a guessed `type` to every note, maps retired statuses to `draft`, turns
backticked paths that name another note into links, and moves the ON files and
`wip.md`. Running it twice is safe.

It prints four lists. Keep the output; steps 4 and 5 work through "Types
guessed", "Needs a decision", and "Mentions of v0.0 machinery".

Notes that git ignores are private to this user. The script updates them like
any other note.

## 3. Configure

```bash
python3 .claude/skills/context-db/context-db.py configure --project <name> --python <command> --main-branch <branch>
```

- `<name>` is the existing project folder's name without the `-project` suffix.
- `<command>` is `python3` unless that is wrong for the team. Ask the user if
  you are unsure. For a path that is right only on their machine, add
  `--local python=<path>`.
- `<branch>` is the repository's main branch, usually `main`. It is not the
  branch you created for this migration.

With these flags `configure` asks nothing. It writes the settings, creates the
missing ON files and `wip/`, adds one line to `.gitignore`, and prints what the
checker found.
It exits with an error when the checker finds problems. That is expected at this
point; steps 4 and 5 fix them.

## 4. Clear out what is obsolete

Do this before fixing checker errors, so that you do not repair notes you are
about to delete.

- **Notes about the v0.0 machinery itself**, such as how the TOC script or the
  resolver works: delete them.
- **Mentions of v0.0 machinery** in notes that are about something else: the
  script listed each one with its line. Rewrite the sentence so that it is true
  for v0.1, using the table above. `maintain` still exists and needs no change.
  If a whole note turns out to be about the old machinery, delete it.
- **The ON files that were moved**: read each one and remove statements that are
  no longer true, such as paths to the old scripts. Their frontmatter is no
  longer needed and can go.
- **`_drafts/` folders** are now ordinary folders. Move live plans into
  `<name>-project/wip/` and delete the rest.
- **The old `wip.md`** is now `wip/current-work.md`, listed in `wip/wip.md`.
  Delete finished items, split the rest one file per effort, and give each a
  line in `wip/wip.md` (start date, branch, status).
- **Folder descriptors**: after deleting notes, check the description in that
  folder's `<folder>.md` and remove topics that are gone.

## 5. Fix what the checker reports

Run this after each round, until it prints no errors:

```bash
python3 .claude/skills/context-db/context-db.py toc --check
```

- **Guessed types.** The guess comes from keywords and defaults to `Reference`.
  Check each against the definitions in `format.md` and correct the ones that
  are wrong.
- **No folder descriptor.** Add `<folder>/<folder>.md` with `type: Folder` and a
  description. Where the script said to rename an old descriptor, rename it and
  set its `type` to `Folder`.
- **No frontmatter.** v0.0 allowed a fenced `yaml description` block instead.
  Convert it to real frontmatter.
- **A value that is not valid YAML.** Reword the description, or wrap it in
  double quotes.
- **Broken links, or links that start with `/`.** Make them relative to the
  file. A link that left a shared folder through `..` has to go, or the target
  has to move inside. If the target is a private note that is not in the
  repository, replace the link with plain text.
- **"does not resolve"** lines from the script are backticked paths it could not
  find. Fix the ones that were meant as references. Leave the ones that are only
  examples.
- **Oversized files and folders** are warnings. Split them when convenient.

If the project formats its Markdown, run the formatter now. Converted links can
push a line past the wrap width.

## 6. Shared folders

The migration script refuses to touch symlinked folders. For each one, go to
the repository that owns it and there:

```bash
python3 <cdb-repo>/context-db/context-db-project/context-db-migrate-from-v0.0/migrate-v0.0.py context-db
python3 <cdb-repo>/skill/context-db/context-db.py toc context-db/<folder> --check
```

Naming the folder means that repository needs no settings of its own. Work
through steps 4 and 5 there, then commit there. The folder is listed here on
demand like any other, before and after.

## 7. Standing instructions, docs, and hooks

Everything in this step is outside `context-db/`.

- Replace the context-db section of `AGENTS.md` or `CLAUDE.md` with
  `.claude/skills/context-db/starters/AGENTS.md`.
- Search the project's own docs, such as the README, for anything in the "What
  changed" table: `read`, the old script paths, `ON_*.md` at the
  root of `context-db/`. Bring each up to date.
- If the project has a pre-commit hook or CI, add
  `<python> .claude/skills/context-db/context-db.py toc --check`, and remove
  any call to the old scripts.

## 8. Verify and commit

```bash
python3 .claude/skills/context-db/context-db.py toc --check
python3 .claude/skills/context-db/context-db.py prompt "test"
```

The first must exit 0 and call the folder a conformant OKF bundle. In the output
of the second, check that:

- the project folder's description says what the project is;
- every background folder is listed, if the project has any;
- each plan under Work In Progress has a description that says what the work is.

Then commit, naming the context-db commit from step 1 in the message. Do not
run `/context-db wip` or `/context-db update` yourself; tell the user they can.
