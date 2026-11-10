---
name: context-db
description:
  'Project knowledge base in Open Knowledge Format. Sub-commands: prompt,
  update, wip, configure. Type help for usage.'
allowed-tools: Bash,Read,Write,Edit,Glob,Grep
---

Run the script with the user's arguments:

    <python> .claude/skills/context-db/context-db.py <args>

`<python>` is the `python` value in `context-db/context-db.local.json` if that
file exists and sets one, otherwise the `python` value in
`context-db/context-db.json`, otherwise `python3`.

Sub-commands: `prompt`, `update`, `wip`, `configure`, `help`. Quote a multi-word
instruction as one shell argument, so that punctuation in it cannot be read as
shell syntax:

    <python> .claude/skills/context-db/context-db.py update "Notes go in the wiki, not the README"

The script prints instructions for you. Follow them.
