---
type: Decision
description:
  The one order in which every command takes the knowledge — work in progress,
  then project knowledge, then knowledge from outside — and how quietly it is
  to be said. Also called the three tiers, or layers.
---

# The order of the knowledge

The owner, 2026-11-24: "The first place to look is the wip, then the project
knowledge, then the extra project knowledge (which can be in the context-db/
folder or anywhere with correct config)". On 2026-11-25 it became the
structure "for all the tools": the wip is "top of mind", and with none, or
none that pertains to the question, "the agent quickly skips".

## What the owner decided

It is to be "brief, subtle concise", "subtely in the design", and "I do not
want you to print this everywhere". So the order shows in how things are
arranged, and is put into words in few places:

- Arranged: the bullets of `update.md`, the sweep in `maintain.md`, the
  sections of each message, and every list, table, and numbered step in the
  docs. A new list of these kinds takes the same order and adds no sentence.
- In words: the three steps of `prompt.md`, "What it is" on the two front
  pages, and the paragraph under the tree on the Layout page.

## The implementing agent's choices

- The docs say "knowledge from outside the project" for the third. The owner
  said "external knowledge", but the front pages already call usage knowledge
  external ([voice.md](./writing-docs/voice.md)).
- A project's own usage folders are read in the third step of `prompt`, and
  written after the project folder by `update` and `maintain`.
- `maintain` checks the plans before the notes, so that what it moves out of
  a finished plan is swept with the rest.

## What trial agents showed

- Each step says when it applies, and every kind of folder has a step. An
  agent could not place a usage folder, and read "Every other folder" as a
  duty to list each.
- When a section can be left out, say what its absence means. With no Work In
  Progress section and a `wip/` folder in the listing, an agent could not
  tell no plans from plans that were not shown (2026-11-25). Hence "Without
  it, there are none."
- The test for opening a note is the same for every folder, or the agent
  passes over standards that apply.
