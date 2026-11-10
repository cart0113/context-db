---
name: context-db
description:
  'Project knowledge base. Sub-commands: prompt, update, wip, configure. Type
  help for usage.'
allowed-tools: Bash,Read,Write,Edit,Glob,Grep
---

Run the script with the user's arguments:

    <python> .claude/skills/context-db/context-db.py <args>

`<python>` is the `python` value in `context-db/context-db.local.json` if that
file exists and sets one, otherwise the `python` value in
`context-db/context-db.json`, otherwise `python3`.

Sub-commands: `prompt`, `update`, `wip`, `configure`, `help`. Pass a multi-word
instruction as one quoted shell argument:

    # WRONG — the shell splits the words and argparse fails:
    <python> .claude/skills/context-db/context-db.py update Notes go in the wiki

    # RIGHT:
    <python> .claude/skills/context-db/context-db.py update "Notes go in the wiki"

The script prints instructions for you. Follow them.
