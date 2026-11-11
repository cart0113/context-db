---
name: context-db
description:
  'Project knowledge base in Open Knowledge Format. Sub-commands: prompt,
  update, wip (optional), configure (a setup helper). Type help for usage.'
allowed-tools: Bash,Read,Write,Edit,Glob,Grep
---

Run the script from the repository root with the user's arguments:

    <python> .claude/skills/context-db/context-db.py <args>

`<python>` is the `python:` line at the top of
`context-db/configuration/settings.local.md` if that file exists and has one,
otherwise the one in `context-db/configuration/settings.md`, otherwise
`python3`.

Sub-commands: `prompt`, `update`, `wip`, `configure`, `help`. Flags such as
`--commit`, `--push`, `--list`, `--cleanup`, and `--clear` go outside the
quotes.

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
