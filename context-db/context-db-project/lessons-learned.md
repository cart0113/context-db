---
type: Gotcha
description:
  Prompt-writing lessons from building context delivery — late-session recall,
  why not to pre-load, rules last and instruction last, testing a prompt on a
  fresh agent, single-quoting instructions, defining every term, cwd-relative
  paths. Read before editing anything under skill/context-db/prompts/.
---

# Lessons Learned

## Late-session recall problem

Context loaded at session start gets compressed away after 15–20 turns. By turn
40 the agent has lost the project's standards. Re-instructing at the moment of
work avoids this, which is why `/context-db prompt` exists and why there is no
startup hook.

## Pre-loading all files breaks the hierarchy

Stuffing every file into the prompt fails: a script cannot judge relevance (that
is a language task), it does not scale, and it bypasses description-based
routing. The script prints where to start; the agent navigates.

## Mandatory rules go last, the user instruction after them

Recency wins. Rules at the top of a composed prompt get diluted by everything
after them. `ON_*.md` content is emitted at the end of each command's output,
immediately before the user instruction, which is always the final section,
even on `update --commit`. The script adds no wording of its own to ON content.
It adds a `# Project Rules` heading only when the file does not start with a
heading, because a test agent read unheaded rules as part of the section above
them.

## Test a prompt change on an agent that has never seen it

Tests and a careful read did not find the problems that three fresh agents found
in their first run. Each got a throwaway project, the one slash command a user
would type, and the rule "read SKILL.md and do what it says", plus a request to
report every place it had to guess, with the wording quoted. That surfaced a
shell-quoting bug, a hole in the YAML check, three undefined words, and a
migration that passed every check while still stating old facts.

Do this again after changing any file in `skill/context-db/prompts/`, `SKILL.md`,
or the migration guide. Tell the agent what a sensible user would answer, so
that it does not stop at every question, and do not tell it what you expect to
see.

One trap when testing by hand: within a session the harness shows the copy of
`SKILL.md` it loaded first. After editing that file, a second `/context-db` call
in the same session still shows the old text. The script and the prompt files
are read fresh every time.

## Tell the agent to single-quote the instruction

`SKILL.md` once showed the instruction in double quotes. The shell then expands
`$` and backticks: "Refunds over $10,000" reached the script as "Refunds over
0,000", with no error. Single quotes, or `-` with the text on standard input,
pass it through untouched.

## Define every word a step depends on

Fresh agents stalled on three undefined words: "landed" in `wip` (merged, or
only committed?), "descriptor" in `configure`, and "settle with the user" (wait,
or proceed?). Each now has a definition or an explicit rule in the prompt. When
adding a step, ask what a reader with no context would have to guess.

## Configure is a menu, not a form

The owner wants `/context-db configure` to feel like a guided helper: one
question at a time, as a menu with a recommended option, using the agent's
question tool where it has one. Add a new setting as a question in
`configure.md` and a setting flag on `configure`, never as something to edit by
hand.

The owner's model of the product, stated on 2026-11-11: context-db supplies the
instructions that keep an agent grounded, the `ON_*.md` files are how a user
controls that behavior, and `configure` is the helper that reads those files,
asks what the user wants changed, and edits them. Docs must say this plainly.

Two more requirements from the owner, the same day. `configure` asks which
other repositories the project relies on, by path or URL, and lists them in
`ON_PROMPT.md`; nothing is cloned and no setting is added. And its closing
summary stays short: the files changed in this run, then the files that control
context-db. Easy matters more than complete; do not let `configure` grow.

## Lead with what to do, then the constraints

A prompt that opens with a list of prohibitions makes weaker models conclude
they cannot help at all. State the job first, constraints after.

## All printed paths are relative to the agent's cwd

Absolute paths and resolved symlinks cause a wrong read followed by a
self-correction. Every path the script prints goes through `rel()`.

## H1 headers delimit sections

No measurable difference between custom bracket tags and Markdown H1 headers for
separating sections of a composed prompt, and headers need no closing tag. Each
prompt file opens with one H1; the script adds H1 sections for dynamic content
(`# Folders`, `# Work In Progress`, `# Git State`, `# User Instruction`).

## Name the project folder on writes, not on reads

Write commands say exactly where to write, because writes need direction. The
`prompt` output lists every folder with equal standing apart from the label,
because reads need recall: narrowing attention to the project folder biases the
agent away from standards that apply.

## Retire a specialized primitive once a flexible one subsumes it

`ON_*.md` files replaced several single-purpose flags and config tiers in v0.0.
Two ways to do one thing means two things to document, test, and choose between.
The same reasoning removed `read` in v0.1. It also removed `maintain`, which was
a mistake, restored on 2026-11-11: an audit and a session's lesson are different
jobs, and folding one into the other made `update` do work when there was
nothing to do. See
[command-set.md](./design-decisions/command-set.md).
