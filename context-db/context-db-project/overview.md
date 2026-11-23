---
type: Reference
description:
  Orientation for agents modifying the context-db codebase — where the skill
  lives, what is generated, what to run after a change. Not an explanation of
  what context-db is; the README covers that.
---

# context-db (project notes)

This repo ships one skill folder, [skill/context-db/](../../skill/context-db/),
and uses it on its own `context-db/`.

- The script, [context-db.py](../../skill/context-db/context-db.py), is the API
  surface. The five user commands print instructions the calling agent follows.
  Two helpers are hidden from `--help`: `toc` lists a folder and, with
  `--check`, checks the format, and `audit` is the second step of
  `prompt --audit`. See [command-set.md](./design-decisions/command-set.md).
- Agent-facing wording lives in `prompts/*.md` and in the triple-quoted
  constants at the top of the script, never inside functions.
- `.claude/skills/context-db` is a symlink to `skill/context-db`. Edit the files
  under `skill/`.
- There are no `index.md` files; `toc` builds listings on demand. After touching
  anything under `context-db/context-db-project/`, run
  `python3 skill/context-db/context-db.py toc --check`. The pre-commit hook and
  CI run it too.
- The docs site includes the prompt files verbatim, so changing a prompt changes
  the docs. See [writing-docs/](./writing-docs/writing-docs.md) before editing docs.
- Run `.venv/bin/python -m pytest tests` after changing the script, a prompt,
  the example, or the migration script. Two tests need PyYAML and are skipped
  without it.
- The example under `example/` is a real, runnable project. Tests execute
  against a copy of it, so keep it lint-clean.
- CI tests on Python 3.8 and 3.13 in the official Docker images, because hosted
  runners no longer provide 3.8. Do not use syntax newer than 3.8 in the script.
  No 3.8 is installed here, but Docker is, so the tests can be run in the
  `python:3.8` image as CI runs them. Its argparse lays `--help` out
  differently: a subcommand as long as `configure` gets a line to itself. A
  test that reads `--help` must not depend on the layout.
  CI also runs `ruff format --check .` and `ruff check .` on the whole
  repository, and the pre-commit hook skips ruff when it is not installed.
- A pull request from someone else: the owner's test (2026-11-23) is that it
  is "safe and does not change the mission of the project". The runs GitHub
  started for PR #1, which came from a fork, failed without starting a job, so
  run the CI steps on the head commit yourself, and merge with
  `--match-head-commit` so that what is merged is what was checked.
- The owner sometimes runs a second agent in this same working tree. Stage your
  own files by name, never everything, and check a shared file's diff in the
  same command that stages it. On 2026-11-11 a commit made moments after a clean
  check still carried the other agent's edit to `docs/index.md`.
