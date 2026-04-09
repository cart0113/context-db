---
name: context-db-manual
description:
  'How to use context-db, a markdown knowledge base containing all project
  context, standards, and knowledge.'
allowed-tools: Bash Read
---

`context-db/` is the project's persistent knowledge base — things that can't be
learned from reading the code alone: gotchas, design decisions, cross-file
patterns, and checklists. It's checked into the repo and available to every
agent, on every platform, in every future session.

Every `.md` file has YAML frontmatter with a `description` field. The TOC script
reads those descriptions so you can browse without opening every file.

## How to read it

Run the TOC script, then read relevant topics:

```
.claude/skills/context-db-manual/scripts/context-db-generate-toc.sh context-db/
```

Skip topics that are clearly irrelevant. When in doubt, read the topic — it's
faster than grepping the entire codebase.

**Context-db is a hint, not truth.** It can be stale, incomplete, or wrong.
Always read the actual source before making changes. Never skip code reading
because context-db "already explained" what you need.

Before acting on context-db claims: if it names a file, check the file exists.
If it names a function or flag, grep for it. If it describes architecture, read
the actual modules. If it provides a checklist, use it as a starting point —
then trace the full integration chain in the code to check for steps the
checklist missed. If context-db conflicts with the code, trust the code.

## What belongs in context-db

Write only what an agent cannot get from reading the code:

- **Gotchas.** Things that look right but break.
- **Cross-file checklists.** "Adding a new X? Touch these 5 files."
- **Why, not what.** Why a decision was made. Why this pattern instead of the
  obvious one.
- **High-level architecture.** How the major pieces connect. One paragraph, not
  a module-by-module walkthrough.

## What does NOT belong

Every line costs tokens. Verbose context-db is worse than none.

- **Code summaries.** Never restate what a class or function does.
- **API signatures or parameter docs.** These belong in docstrings.
- **Module layouts.** `ls` and `grep` are faster than a markdown tree.
- **Anything the code already makes obvious.**

## Writing format

Every `.md` file requires frontmatter:

```yaml
---
description: One-line summary shown in the TOC
---
```

Two file types:

- **Documents** — frontmatter + body content.
- **Folder descriptions** (`<folder-name>.md`) — frontmatter only, no body.

Descriptions must be accurate summaries — not titles. A reader must be able to
judge relevance without opening the file.

Most content goes in `<project-name>-project/`. Parallel top-level folders
(`coding-standards/`, `writing-standards/`) are project-agnostic and often
symlinked from a shared repo.

When a document relates to other files, add a "See also" section with links.

## Maintenance

Keep 5-10 items per folder. After changes, rewrite affected descriptions. Run
`context-db-generate-toc.sh` on affected folders to verify. Details are in
`context-db/using-context-db/`.
