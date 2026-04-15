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
and framing the prompt as data in the system prompt (`[main-user-prompt]`).

## Positive-first role framing for sub-agents

Leading with DO NOT constraints ("You do NOT perform tasks, do NOT write code,
do NOT run git") made haiku refuse to navigate entirely — it concluded it
couldn't help and returned nothing useful. The fix: lead with the positive job
description ("Your job is to find all relevant context from context-db"), then
add constraints after. The model needs to know what it SHOULD do before hearing
what it shouldn't.

## Combined role blocks work, scattered constraints don't

Splitting identity, task description, and navigation constraints across separate
tagged blocks caused coherence issues — the model lost the connection between
"what I am" and "what I'm supposed to do." One combined `[sub-agent-role]` block
per command, containing identity + task + constraints, keeps the sub-agent on
track. Per-command variants are needed because "what to find" differs (prompt:
applicable context, pre-review: applicable standards, review: convention
violations).

## Content-first ordering matters

Prompt before navigation instructions produces better results. The model reads
what it needs context for, then navigates with that filter in mind.

For sub-agents, this means injecting the developer's prompt into the system
prompt as a labeled data block (`[main-user-prompt]`) before the role
instructions. The role then references it: "find context for the
[main-user-prompt] above." This frames the prompt as a search query — the model
sees what to look up before being told how. Without this, cheap models treat the
prompt as a task and execute it (e.g. running `git commit` when the prompt says
"Commit").

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
