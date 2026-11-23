---
name: context-db
description:
  'Project knowledge base in Open Knowledge Format. Sub-commands: prompt,
  update, wip (optional), maintain, configure (run it first). Type --help for
  usage.'
allowed-tools: Bash,Read,Write,Edit,Glob,Grep
---

Run the script from the repository root with the user's arguments:

    <python> <skill>/context-db.py <args>

`<skill>` is the folder this file is in, as a path from the repository root,
such as `.claude/skills/context-db` or `.codex/skills/context-db`.

`<python>` is the `python:` line at the top of
`context-db/configuration/settings.local.md` if that file exists and has one,
otherwise the one in `context-db/configuration/settings.md`, otherwise
`python3`.

Sub-commands: `prompt`, `update`, `wip`, `maintain`, `configure`. With no
sub-command, or with `--help`, the script prints the list. Flags the user
typed on the command's line, such as `--push`, `--list`, and
`--show-context`, go outside the quotes. With no instruction, pass only the
flags.

The user's instruction is everything else they typed, most often on the lines
below the command. Pass it exactly as they typed it, line breaks included, as
one single-quoted argument. Single quotes stop the shell from changing `$`,
backticks, and `!`:

    <python> <skill>/context-db.py update 'Refunds over $10,000 need approval' --push

If the instruction itself contains a single quote, pass `-` in its place and
feed the text on standard input:

    <python> <skill>/context-db.py update - --push <<'EOF_INSTRUCTION'
    Don't retry refunds; they aren't idempotent
    EOF_INSTRUCTION

The script prints instructions for you. Follow them. They may tell you to run
`configure` with setting flags in the same way.

Apart from reading that `python:` line, whenever you look into `context-db/`
or any other knowledge folder the script names, list the folder with the `toc`
helper, run the same way: `<python> <skill>/context-db.py toc <folder>`.
It builds the folder's index from its files on the spot. `toc --check` checks
the format after you write.
