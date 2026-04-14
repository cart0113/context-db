---
description:
  Lessons from building context delivery — late-session recall, pre-loading
  pitfalls, prompt engineering for cheap models, relative paths. Applies to the
  unified /context-db skill.
---

# Lessons Learned

## Late-session recall problem

Context loaded at session start gets compressed away after 15-20 turns. By turn
40, the agent has lost standards. Re-instructing on every call avoids this.

## Pre-loading all files breaks the B-tree

Stuffing every `.md` file into the prompt fails: Python can't judge relevance
(that's a language task), doesn't scale, and bypasses description-based routing.
Let the agent navigate the hierarchy.

## Cheap models need structured output constraints

Haiku ignores "do NOT help with the task" — it treats the user's prompt as its
own task. Fix: structured output format ("respond with ONLY verbatim snippets")
and wrapping the prompt as `Developer's prompt: <text>` to reframe it as a
lookup, not a task.

## Content-first ordering matters

Prompt before navigation instructions produces better results. The model reads
what it needs context for, then navigates with that filter in mind.

## The rule file is the durable anchor

The session-start hook fires once. SKILL.md loads on demand. The rule file stays
in context all session — it survives compression. Durable instructions go there.

## Constrain navigation to TOC + Read only

Without constraints, haiku adds `find`, `ls -la`, `head -50` that waste turns.
"Do not use find, grep, or ls" produces clean 2-3 step navigation.

## All paths must be relative to cwd

Absolute paths and symlink resolution cause double-reads (wrong path, then
self-correction). All paths relative to cwd: TOC script is
`.claude/skills/.../context-db-generate-toc.py`, context-db is `context-db/`.

## Feed standards before agents start, not at session start

Standards loaded at session start fade. Pre-review mode forces the agent to
fetch standards _immediately before starting edits_ — a structural fix.

## Do not anthropomorphize in prompts

Frame sub-agent responses as "additional context" — not advice from a junior to
a senior. The goal is to inform, not establish hierarchy.

## Self-reference guard

Without scope filtering, the subagent returns information about context-db
itself when asked about a project that uses context-db. Constrain to information
found in the knowledge base, not about the knowledge base system.
