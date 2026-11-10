---
name: context-db
description:
  'Project knowledge base in Open Knowledge Format. Sub-commands: prompt,
  update, wip, configure. Type help for usage.'
allowed-tools: Bash,Read,Write,Edit,Glob,Grep
---

Run the script from the repository root with the user's arguments:

    <python> .claude/skills/context-db/context-db.py <args>

`<python>` is the `python` value in `context-db/context-db.local.json` if that
file exists and sets one, otherwise the `python` value in
`context-db/context-db.json`, otherwise `python3`.

Sub-commands: `prompt`, `update`, `wip`, `configure`, `help`. Flags such as
`--commit` and `--push` go outside the quotes.

Pass the user's instruction exactly as they typed it, as one single-quoted
argument. Single quotes stop the shell from changing `$`, backticks, and `!`:

    <python> .claude/skills/context-db/context-db.py update 'Refunds over $10,000 need approval' --push

If the instruction itself contains a single quote, pass `-` in its place and
feed the text on standard input:

    <python> .claude/skills/context-db/context-db.py update - --push <<'EOF_INSTRUCTION'
    Don't retry refunds; they aren't idempotent
    EOF_INSTRUCTION

The script prints instructions for you. Follow them. They may tell you to run
two helper sub-commands, `init` and `index`, in the same way.
