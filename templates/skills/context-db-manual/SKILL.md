---
name: context-db-manual
description:
  'How to use context-db, a markdown knowledge base containing project context,
  architecture, gotchas, and design decisions.'
allowed-tools: Bash Read
---

`context-db/` is this project's knowledge base. It documents architecture,
gotchas, design decisions, and cross-file connections — things you can't learn
from reading any single file. It does not contain everything — it's a starting
point, a map, a hint — but it helps you orient yourself in a project quickly.

## Reading

Browse what's available with the TOC script:

```
.claude/skills/context-db-manual/scripts/context-db-generate-toc.sh context-db/
```

Every file and folder has a `description` in its YAML frontmatter. By calling
the TOC script on a folder, you get a list of descriptions for every file and
subfolder in that folder. Use these descriptions to decide what to read next and
what to skip — drill into topics relevant to your task, ignore the rest. You do
not need to read every file in a folder, only the ones that are relevant based
on their `description` frontmatter.

## Format

Every `.md` file needs YAML frontmatter with a `description` field. This is the
routing decision — an agent reads it to decide whether to open the file. Be
specific: "scheduler tool execution flow, budget enforcement hook" not
"Architecture overview."

Two types: documents (frontmatter + body) and folder descriptors (frontmatter
only, named `<folder-name>.md`).

Keep 5–10 items per folder. Keep files between 50–150 lines, 200 max. If a file
exceeds 200 lines, split it into a subfolder with the same name — the file
becomes the folder descriptor and the content splits into smaller files. After
changes, run the TOC script on the containing folder to verify. Context-db is a
B-tree — agents read descriptions at each level and branch into the relevant
folder, narrowing by 5–10x per level. An agent should reach any topic in 2–3
navigation steps.

## Updating

After completing a coding task, update context-db with what you learned that
would help the next agent working in this area. The main goal is to make things
easier for the next agent. Record critical information, but be concise — useful
for the next LLM who has to cover the same code or problem.

Update existing files when they cover the topic. Create new files for new
topics. Keep notes concise — every token costs.

Reorganize files/folders and create hierarchy when a folder gets too big.
Maintain the B-tree property — 5–10 items per level, 2–3 levels deep.

## What belongs

- **What exists.** Subsystem inventory. Prevents reimplementation.
- **Where to look.** File landmarks, reference implementations.
- **What breaks.** Gotchas, ripple effects, files that must change together.
- **Why.** Design rationale invisible in the code.

## What does NOT belong

- Code summaries, API signatures, module layouts — the agent reads the source.
- Step-by-step instructions — point to reference implementations instead.
