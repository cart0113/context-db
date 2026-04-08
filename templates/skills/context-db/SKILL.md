---
name: context-db
description:
  'How to use context-db, a markdown knowledge base containing all project
  context, standards, and knowledge.'
allowed-tools: Bash Read
---

## What context-db is

`context-db/` is a hierarchical Markdown knowledge base that lives in the
project repo. It contains everything you need to understand this project —
architecture, conventions, standards, domain context, design decisions, user
preferences. Think of it as the project's long-term memory.

Every `.md` file has YAML frontmatter with a `description` field. A script reads
those descriptions and generates a table of contents for any folder. You browse
the TOC, read only what's relevant, and move on.

## Why this matters

You are starting a conversation with no prior context. The knowledge base exists
so you don't have to rediscover what the team already knows. Reading it first
means you write code that fits the project's patterns, follow the right
conventions, and avoid repeating past mistakes.

Skip it and you'll waste tokens guessing at things that are already documented.

## How to read it

Run the TOC script on the root folder:

```
${CLAUDE_SKILL_DIR}/scripts/context-db-generate-toc.sh context-db/
```

The output lists every subfolder and file with a one-line description. Subfolder
paths end with `/` — run the script on them to go deeper. Only open files whose
descriptions are relevant to your task.

**Do this at the start of every conversation.** Read topics relevant to the
user's request before writing code or making suggestions.

## How to write to it

Every `.md` file requires frontmatter:

```yaml
---
description: One-line summary shown in the TOC
---
```

Optional: `status: draft | stable | deprecated` (default: `stable`).

Two file types:

- **Documents** — frontmatter + body content.
- **Folder descriptions** (`<folder-name>.md`) — frontmatter only, no body.
  Registers the folder in the parent TOC.

Descriptions must be accurate, complete summaries — not titles. An agent must be
able to judge relevance without opening the file.

## How to maintain it

**5–10 items per folder.** When a folder exceeds this, split into subfolders.
The tree is a decision tree — each level should halve the search space.

**Keep descriptions current.** After any change, rewrite every affected
`description` to match current content.

**Post-session checklist:**

1. Capture — create or update documents with new knowledge.
2. Summarize — rewrite affected descriptions.
3. Reorganize — split or merge folders to stay at 5–10 items.
4. Verify — run `context-db-generate-toc.sh` on affected folders.
