---
type: Decision
description:
  The five user commands and their order, and why — no flag narrows prompt,
  update, or maintain, because a command is only a starting point; maintain
  apart from update; configure, not init; --show-context, not --dry-run;
  prompt --audit; one source for the summaries and the API block. Owner
  decisions.
---

# The command set

The owner fixed the set on 2026-11-11 and the order on 2026-11-23: `prompt`,
`update`, `wip`, `maintain`, `configure`. "configure should always be listed
last." Use that order everywhere a list of commands appears.

## No flag narrows a command

The owner, 2026-11-23: "I do not want all these switches. By default, prompt,
update, maintain do everything and touch project (including wip) and usage",
and "if you just want to focus on one or the other, just talk to the agent."
context-db is "just a starting point", the common defaults that open a
conversation, and the user shapes the rest in words. The owner wants the docs
to say so: under the API block on the front page, and on the commands page.

- Do not add a flag that narrows what a command looks at or changes how it
  works. `--wip`, `--usage`, `--use-git-diff`, and `--use-global-context` were
  all built and then removed. A flag stays only when it does something a
  sentence should not: `--commit` and `--push`, the three modes of `wip`, and
  `--audit` on `prompt` (below).
- `update` goes by what the agent remembers of the session and reads no git.
  It also keeps the plan that the session worked from current, and must be
  very brief about it.
- `maintain` always gets the git history, and the state of git when there are
  plans. The owner: for `maintain`, "it's assumed to use version control".
- `wip --list`, `--maintain`, and `--clear` are the owner's. `--maintain` was
  `--cleanup`: the sweep of every plan, judged by version control. Plain
  `maintain` makes the same check as part of its sweep.
- Narrowing in words does not shorten the message. The script cannot read the
  instruction, so the agent skips the sections that are out of scope.

Before changing what the commands or flags are, show the owner the whole of it
as typed, as the `API` block, and wait. A full build of scope flags on every
command was thrown away the day it was made. Wording that the owner dictates
for the block is different: make the change, and show the whole block in the
reply.

## maintain is a command again

v0.1 had dropped it in favour of `update "audit <folder> and cut"`. The owner
restored it. Mixing "write down this session's lesson" with "clean up the
knowledge base" made `update` do work when there was nothing to do. So:

- `update` changes only the files its lesson belongs in, leaves format problems
  in other files alone, and stops in one line when there is nothing to change.
  Since 2026-11-22 it also fixes or deletes the notes that the session itself
  showed to be wrong or not needed, and names any others it noticed and asks.
  An agent that a note has just misled is the one that knows the note is wrong.
- `maintain` does sweeps, checks first, and stops when nothing needs changing.
  Its main job is enforcing the no-duplication rule (below), and its second
  the keep-small rule.

`configure` asks how freely `update` cleans up. That is the implementing
agent's choice: the owner said only that asking the user how far to go is fine
and "could be a config option". The question writes a sentence into
`ON_UPDATE.md` for an answer other than the default, so the default costs
nothing on each run.

## configure, not init

The owner: "init and configure are the same thing". `configure` with no flags
starts the conversation; with `--project` or any other setting flag it writes
the files and asks nothing. There is no `help` sub-command; `--help` and a bare
call print the list. `toc` is left out of `--help` because only the agent and
CI run it.

## --show-context, not --dry-run

The owner (2026-11-19) wanted "a --dry-run" on every command and rejected the
name in the same sentence: "all this does is invoke the skill and show what
context will be sent to the agent". Nothing is simulated, so the flag is named
for what it does. `--show-context` was the implementing agent's proposal, and
the owner kept it.

The message between the markers must stay byte for byte what the command sends
without the flag. The flag is refused together with `configure`'s setting
flags, because showing must never write.

## prompt --audit

The owner asked for it on 2026-11-23, for whoever designs a knowledge base:
"see what information the agent grabbed" and "what breadcrumbs", output "to
the window and then do the actual prompt". A separate `audit` command was set
aside for now; whether to list one, for an audit after the fact, is open.

The owner's condition: no "Schrodinger's cat problem", "we want to see what
is going to really happen and what would have been used". A first build
described the report in the `prompt` message, and a trial agent skipped a
link "to avoid reading more for the sake of the report". So the message only
says to run the hidden `audit` helper once the reading is done, and the
helper says what to report. Keep every word about the report out of the
`prompt` message. A sentence typed with the task would have the same fault.

The helper, the second report after the work, and what the reports hold are
the implementing agent's choices. The `API` line and the workflow on the
Commands page (the audit, then `maintain`) the owner asked for.

## One source for the summaries and the API block

`COMMAND_SUMMARIES` in the script is what `--help` shows, and a bullet list on
the README and on the docs home page repeats it word for word. A test compares
all three and the section headings of `docs/commands.md`. Change the summary
in the script, then copy it to both pages. The list was a table and a row of
colored cards until 2026-11-23, when the owner said: "Not sure we need these
as callout boxes, just a bullet list."

`API` in the script is what the user types, in one block. The owner asked for
"a code block ... which shows the whole api on the front page". `--help`
prints it, both front pages repeat it, and a test compares them.

- Its placeholders are the owner's (2026-11-23): `<prompt: question or task>`
  and `<steering-guidance>`. So is the description of `prompt`: "Navigate the
  context-db open knowledge format md files based on the contents of the
  prompted question or task".
- `--commit` and `--push` are left out of the block, the summaries, and both
  front pages. The owner: "very inside baseball", a "personal preference not a
  necessary feature", to be "left to the inner docs as helpful workflow". The
  Commands page and `update --help` describe them. Dropping them from the
  top-level `--help` too was the implementing agent's choice, so that the
  front pages still repeat it word for word.

## Shared core text

Two prompt files go to the agent on every command that reads or writes notes,
so the system says one thing everywhere: `no-duplication.md` (context-db never
restates what the code and its comments say) and `navigate.md` (see
[dynamic-index.md](./dynamic-index.md)). The owner asked for the no-duplication
rule to be stressed uniformly "throughout and in our main page, the motivation
section". Edit the rule in that file, and keep the docs' wording of it in step.

A third, `keep-small.md`, goes with every command that writes. The owner asked
for it on 2026-11-22: agents "are too verbose", they duplicate and "write too
much for the problem at hand", so `update` and `wip` need "concise
instructions" that the agent is also keeping the knowledge base minimal, and
"it's ok for agents to ask for guidance on this". The owner's reason: an agent
is trained on the task in front of it and does not weigh what a note costs
later, so the long view has to come from the instructions. The wording of the
rule, the warning for a description over 300 characters, and the first-line
"Delete this once ..." sentence are the implementing agent's choices.
