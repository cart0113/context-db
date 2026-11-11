---
type: Decision
description:
  Why there is a committed context-db.json plus a gitignored
  context-db.local.json, why the interpreter is a config value the agent reads
  rather than something the script resolves, and why the key set is closed
---

# Config layering

v0.0 had no config. v0.1 has four keys, because each answers a question the
script cannot reliably answer itself:

- `project` names the project folder, so nothing has to glob for `*-project/`.
- `python` is the interpreter. On some machines `python3` is too old or absent.
- `main_branch` is the diff base for `/context-db wip`.
- `update_mode` records the owner's answer to "who updates the knowledge base":
  `on-command` (only on `/context-db update`) or `agent-decides`. The owner
  asked on 2026-11-11 for `configure` to ask this and to deliver the answer
  through `ON_PROMPT.md`. So `init` writes a marked paragraph there, where the
  user can reword it, and replaces it only when `--update-mode` is passed. The
  fixed "do not run update yourself" line was removed from `update.md`, because
  it would contradict `agent-decides`.

## Two files

`context-db/context-db.json` is committed and shared.
`context-db/context-db.local.json` is gitignored; any key in it overrides the
shared value for one user. The typical use is an interpreter path that exists
only on one machine. `init` adds the local file to `.gitignore`.

## The interpreter is read by the agent

The script cannot choose the interpreter that runs it. So `SKILL.md` tells the
agent where to find the value: local file, then shared file, then `python3`.
The script then prints follow-up commands with the configured interpreter
already filled in.

`configure` runs before any config exists, so it reports what it can see: the
interpreter running it, and whether `python3` on PATH is the same one or new
enough. It must keep working when the config is missing, partial, or not valid
JSON, because it is the repair tool; the other commands stop with an error.

## The key set is closed

`CONFIG_KEYS` in the script is the whole schema. A new key needs the same
justification as the first three: something the script cannot work out, that a
user would otherwise have to restate.
