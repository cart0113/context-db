---
type: Gotcha
description:
  Prompt-writing lessons from building context delivery — late-session recall,
  why not to pre-load, rules last and instruction last, positive framing first,
  cwd-relative paths, and retiring specialized primitives. Read before editing
  anything under skill/context-db/prompts/.
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
even on `update --commit`. The script adds no framing around ON content; its
author owns the wording.

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
The same reasoning removed `maintain` and `read` in v0.1: lint moved into the
`index` helper, and an audit is `update "audit <folder> and cut"`.
