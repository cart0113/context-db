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
and framing the prompt as data in the system prompt (`# Main Prompt`).

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
"what I am" and "what I'm supposed to do." One combined `# Sub Agent Role`
section per command, containing identity + task + constraints, keeps the
sub-agent on track. Per-command variants are needed because "what to find"
differs (prompt: applicable context, pre-review: applicable standards, review:
convention violations).

## Content-first ordering matters

Prompt before navigation instructions produces better results. The model reads
what it needs context for, then navigates with that filter in mind.

For sub-agents, this means injecting the developer's prompt into the system
prompt as a labeled data block (`# Main Prompt`) before the role instructions.
The role then references it: "find context for the `# Main Prompt` above." This
frames the prompt as a search query — the model sees what to look up before
being told how. Without this, cheap models treat the prompt as a task and
execute it (e.g. running `git commit` when the prompt says "Commit").

## Review sub-agents need different constraints than lookup sub-agents

Prompt and pre-review sub-agents are pure knowledge lookups — lock them to TOC
script + Read only. Review sub-agents need to read source files, run git diff,
and potentially grep for patterns. Only ban destructive commands (git add,
commit, push, reset). Over-constraining review breaks it; under-constraining
lookup lets haiku run wild.

## Self-review catches real bugs

Running the review sub-agent against its own changes (with sonnet) caught an
IndexError bug where the `# Main Prompt` injection split failed when the role
template was the first in the composition. Sonnet is the right model for review
— haiku lacks the reasoning depth to compare code against conventions.

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

## H1 markdown headers work as well as custom bracket tags

No performance difference between `[tag-name]...[end tag-name]` and `# Tag Name`
for section delimitation. LLMs are trained extensively on markdown — H1 headers
are among the most common structural tokens in training data. H1 headers are
more human-readable, need no closing tag, and use standard formatting. One H1
per template file; sub-sections use H2/H3.

## Self-reference guard

Without scope filtering, the subagent returns information about context-db
itself when asked about a project that uses context-db. Constrain to information
found in the knowledge base, not about the knowledge base system.
