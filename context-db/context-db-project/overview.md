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
  surface. The four user commands print instructions the calling agent follows;
  `init` and `index` are helpers that do the file work.
- Agent-facing wording lives in `prompts/*.md` and in the triple-quoted
  constants at the top of the script, never inside functions.
- `.claude/skills/context-db` is a symlink to `skill/context-db`. Edit the files
  under `skill/`.
- Every `index.md` is generated. After touching anything under
  `context-db/context-db-project/`, run
  `python3 skill/context-db/context-db.py index`. The pre-commit hook and CI run
  it with `--check`.
- The docs site includes the prompt files verbatim, so changing a prompt changes
  the docs. See [writing-docs/](./writing-docs/index.md) before editing docs.
- Run `.venv/bin/python -m pytest tests` after changing the script, a prompt,
  the example, or the migration script. One test needs PyYAML and is skipped
  without it.
- The example under `example/` is a real, runnable project. Tests execute
  against a copy of it, so keep it lint-clean.
- CI tests on Python 3.8 and 3.13 in the official Docker images, because hosted
  runners no longer provide 3.8. Do not use syntax newer than 3.8 in the script.
