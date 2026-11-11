---
type: Convention
description:
  How the docs and README must read — plain, clear, simple, not AI-sounding; no
  first person; the words to use (project folder, background folder, skills);
  how to show a command in an example (instruction on a new line, never in
  quotes). Owner feedback from 2026-11-10 and what it means in practice.
---

# Voice

## What the owner asked for

On 2026-11-10 the repository owner said of earlier docs: "I have found them very
AI written, not clear. I just want it clear simple." And: "Really, this is a set
of skills, be clear what it is."

## What that means in practice

This list is an interpretation of that feedback, drawn from what was removed in
the v0.1 rewrite of the docs.

- Say what a thing is in the first sentence, in everyday words. "context-db is a
  set of skills that you install in a coding agent."
- Show a concrete example before explaining an idea: the folder, a file, the
  command the user types.
- Describe commands as steps the agent takes, in a numbered list.
- No slogans and no bold lead-in phrase at the start of each bullet.
- No em dashes in prose. Use a full stop or a comma.
- No "not X but Y" constructions and no lists of three for rhythm.
- No filler words: simply, just, seamlessly, powerful, robust, deliberately.
- Prefer a paragraph or a small table to a page of tiny headed sections.

## Showing a command

The owner types the command on its own line, then a blank line, then the
instruction, and never puts the instruction in quotes: "I always new line, never
quote" (2026-11-11). Every example of a `/context-db` command is written that
way, in the docs, the README, and the prompt files:

    /context-db prompt

    Users report a bug here: ...

Flags stay on the command's line. Only the terminal form keeps quotes
(`context-db.py prompt "..."`), because the shell needs them.

## Person

No "we" or "I". Address the reader as "you". "Copy the skill into your project",
not "We recommend copying the skill."

## Words

| Use | Not |
| --- | --- |
| project folder | project bundle |
| background folder | background bundle, external folder |
| a set of skills | a tool, a framework, a system |
| settings | configuration (except for the file name) |
| knowledge base | database, store |

"Bundle" and "concept" are OKF's words. Use them only on the OKF page and when
explaining how context-db maps onto OKF. The same vocabulary applies to the
prompt files, because the docs include them verbatim.
