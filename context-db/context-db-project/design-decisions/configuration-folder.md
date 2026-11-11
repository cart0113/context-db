---
type: Decision
description:
  Why every setting and rule is plain Markdown in context-db/configuration/
  (settings.md plus gitignored settings.local.md, the ON files), why there is
  no update_mode key, why configure is only a helper, why the interpreter is
  read by the agent, and why the settings key set is closed. Owner decisions of
  2026-11-11; also called config layering.
---

# The configuration folder

The owner's framing (2026-11-11): "it's all just text that LLM needs to read,
we are just being smart about snippets of text to feed the LLM during targeted
operations." So everything the user controls is a Markdown file in
`context-db/configuration/`, edited by hand. JSON was dropped.

## Settings

`settings.md` holds `project`, `python`, `main_branch` as `key: value` lines in
its frontmatter, parsed by the same frontmatter reader as every note; the body
is free for the user's notes and `configure` preserves it. `settings.local.md` is
gitignored and overrides any key for one user (typically an interpreter path).

The key set is closed: each key answers something the script cannot work out.
A new key needs that same justification.

## No update_mode

"Who updates the knowledge base" used to be a config key that setup wrote as a
marked block into `ON_PROMPT.md`. It is now ordinary text in `ON_PROMPT.md`.
The starter ships the owner's recommended default, update as you go after
`prompt`; `configure` swaps in the on-command paragraph if asked. Behaviour
that is only words for the agent belongs in an ON file, not in settings.

The other recommended defaults: the agent reads `context-db/` only when a
`/context-db` command runs (the AGENTS.md/CLAUDE.md note says so).

## configure is a helper

The owner does not want a settings subsystem: configure is "a conversation
starter". It asks a few questions, edits the files directly as answers come,
and must end by telling the user it only wrote a first draft to hand-edit.
Do not grow it into something that owns state the user cannot see in the files.

## The interpreter is read by the agent

The script cannot choose the interpreter that runs it, so `SKILL.md` tells the
agent to read the `python:` line (local file, then shared, then `python3`). The
script then prints follow-up commands with it filled in. Starter ON files that
name the script get the shared interpreter substituted once, when `configure`
creates them, since they are committed.

`configure` must keep working when settings are missing or broken, because it
is the repair tool; the other commands stop with an error.
