---
name: context-db-manual
description:
  'How to use context-db, a markdown knowledge base containing all project
  context, standards, and knowledge.'
allowed-tools: Bash Read
---

`context-db/` is the project's knowledge base — gotchas, design decisions,
cross-file connections, and what already exists. Checked into the repo,
available to every agent, every session.

Every `.md` file has YAML frontmatter with a `description` field. The TOC script
reads descriptions so you can browse without opening every file.

## How to read it

```
.claude/skills/context-db-manual/scripts/context-db-generate-toc.sh context-db/
```

Read relevant topics. Skip what's clearly irrelevant.

**Context-db is a hint, not truth.** It can be stale, incomplete, or wrong. It
gives you a map — you still have to read the code. If it names a file, check it
exists. If it points to a reference implementation, read that implementation
end-to-end. If it conflicts with the code, trust the code.

## First, do no harm

Context-db gives agents confidence. Confidence reduces code reading. If
context-db is wrong, stale, or too instructional, the agent makes mistakes it
wouldn't have made without it. Keep it small. Keep it current. Point to code,
don't replace it.

## What belongs

A map, not a substitute for reading. Small and focused beats comprehensive.

- **What exists.** Subsystem inventory. Prevents reimplementation.
- **Where to look.** File landmarks, reference implementations to follow.
- **What breaks.** Gotchas, ripple effects, non-obvious files that must change
  together but won't show up in a grep.
- **Why.** Design rationale invisible in the code.

## What does NOT belong

- **Code summaries.** The agent reads the source.
- **Step-by-step instructions.** The agent reads reference implementations.
  Instructions create blind spots — the agent follows steps and misses anything
  not listed.
- **API signatures, module layouts.** `ls`, `grep`, and docstrings are better.

## Format

Every `.md` needs frontmatter with a `description` — this is the routing
decision an agent uses to skip or read the file. Be specific: "cli/core split,
tool execution flow, model routing" not "Architecture overview."

Two types: documents (frontmatter + body) and folder descriptors (frontmatter
only, named `<folder-name>.md`).

Keep 5-10 items per folder. After changes, rewrite descriptions and run the TOC
script to verify.
