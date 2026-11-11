---
type: Decision
description:
  The five user commands and their order (prompt, update, wip, configure,
  maintain), why maintain is separate from update, why init folded into
  configure, why help and the toc helper are not listed, and how --help, the
  README, and the docs home page stay word-for-word in sync. Owner decisions of
  2026-11-11.
---

# The command set

The owner fixed the set and the order on 2026-11-11: `prompt`, `update`, `wip`,
`configure`, `maintain`. Use that order everywhere a list of commands appears.

## maintain is a command again

v0.1 had dropped it in favour of `update "audit <folder> and cut"`. The owner
restored it. Mixing "write down this session's lesson" with "clean up the
knowledge base" made `update` do work when there was nothing to do. So:

- `update` changes only the files its lesson belongs in, leaves format problems
  in other files alone, and stops in one line when there is nothing to store.
- `maintain` does sweeps, checks first, and stops when nothing needs changing.
  Its main job is enforcing the not-a-mirror rule (below). `--use-git-diff`
  adds each note's age against the commits made to the project since.

## configure, not init

The owner: "init and configure are the same thing". `configure` with no flags
starts the conversation; with `--project` or any other setting flag it writes
the files and asks nothing. There is no `help` sub-command; `--help` and a bare
call print the list. `toc` is left out of `--help` because only the agent and
CI run it.

## One source for the one-line summaries

`COMMAND_SUMMARIES` in the script is what `--help` shows, and the README table
and the docs home page cards repeat it word for word. A test compares all three
and the section headings of `docs/commands.md`. Change the summary in the
script, then copy it to both pages.

## Shared core text

Two prompt files go to the agent on every command that reads or writes notes,
so the system says one thing everywhere: `not-a-mirror.md` (context-db never
restates what the code and its comments say) and `navigate.md` (see
[dynamic-index.md](./dynamic-index.md)). The owner asked for the not-a-mirror
rule to be stressed uniformly "throughout and in our main page, the motivation
section". Edit the rule in that file, and keep the docs' wording of it in step.
