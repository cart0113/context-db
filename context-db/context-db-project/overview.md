---
type: Reference
description:
  Orientation for agents modifying the context-db codebase — where the skill
  lives, what is generated, what to run after a change. Not an explanation of
  what context-db is; the README covers that.
---

# context-db (project notes)

This repo ships one skill folder, [skill/context-db/](../../skill/context-db/),
and dogfoods it on its own `context-db/`.

- The script, [context-db.py](../../skill/context-db/context-db.py), is the API
  surface. User-facing commands print instructions the calling agent follows;
  `init` and `index` are helpers that do deterministic file work. Agent-facing
  wording lives in `prompts/*.md`, not in the script.
- `.claude/skills/context-db` is a symlink to `skill/context-db`. Edit the files
  under `skill/`.
- Every `index.md` is generated. After touching anything under
  `context-db/context-db-project/`, run
  `python3 skill/context-db/context-db.py index`. The pre-commit hook and CI run
  it with `--check`.
- The docs site includes the prompt files verbatim, so changing a prompt changes
  the docs. Build with `sphinx-build -W docs docs/_build/html`.
- Run `python3 -m pytest tests` after changing the script or a prompt.
- The example under `example/` is a real, runnable project. Tests execute
  against a copy of it, so keep it lint-clean.
