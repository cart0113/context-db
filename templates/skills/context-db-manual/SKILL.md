---
name: context-db-manual
description:
  'How to use context-db, a markdown knowledge base containing all project
  context, standards, and knowledge.'
allowed-tools: Bash Read
---

## What context-db is

`context-db/` is the project's persistent knowledge base — a hierarchical
Markdown store of everything that can't be learned from reading the code alone.
Gotchas, design decisions, cross-file patterns, and checklists live here.

**context-db is the project's memory.** If you learned something this session
that the next session would need — a gotcha, a decision, a pattern — write it to
context-db. It's checked into the repo and available to every agent, on every
platform, in every future session.

Every `.md` file has YAML frontmatter with a `description` field. A script
generates a table of contents from those descriptions.

## How to read it

Run the TOC script on the root folder:

```
.claude/skills/context-db-manual/scripts/context-db-generate-toc.sh context-db/
```

Read topics relevant to the user's request. Skip what you don't need.

**Context-db orients you. The code is the truth.** Use context-db to understand
the big picture, learn gotchas, and find the right files. Then read the actual
source before making changes. Context-db can be incomplete or stale — always
verify against the code.

## What belongs in context-db

Write only what an agent cannot get from reading the code:

- **Gotchas.** Things that look right but break. Past bugs. Non-obvious ordering
  requirements.
- **Cross-file checklists.** "Adding a new X? Touch these 5 files in this
  order." The code shows how each file works, but not which files must change
  together.
- **Why, not what.** Why a decision was made. Why this pattern instead of the
  obvious one. The code shows _what_; context-db explains _why_.
- **Architecture at the highest level.** How the major pieces connect. One
  paragraph, not a module-by-module walkthrough.

## What does NOT belong in context-db

Every line of context-db costs tokens to read. Verbose context-db is worse than
no context-db — the agent wastes turns reading summaries of code it could read
directly in less time.

- **Code summaries.** Never restate what a class or function does. Reading a
  200-line source file is faster and more complete than reading prose about it.
- **Property lists, API signatures, parameter docs.** These belong in
  docstrings.
- **Module layouts.** `ls` and `grep` are faster than a markdown tree diagram.
- **Anything the code already makes obvious.** If you have to ask "could an
  agent figure this out by reading the file?" the answer is almost always yes.

## How to write to it

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

### Cross-references

When a document relates to other project files — other context-db documents,
source code, docs pages, config files — add a "See also" link at the bottom of
the body.

```markdown
See also:

- [Related context-db topic](../other-folder/file.md)
- [Implementation](../../src/auth/tokens.ts)
- [User-facing docs](../../docs/src/guide/authentication.md)
```

### Where to put new content

**Most content goes in `<project-name>-project/`.** This is the default home for
project-specific knowledge — design decisions, gotchas, architecture, research,
checklists. When adding a new topic, put it here unless it clearly belongs
elsewhere.

Parallel top-level folders (like `coding-standards/`, `writing-standards/`)
contain project-agnostic standards, often symlinked from a shared repo. These
are the exception, not the rule — do not create new top-level folders for
project-specific content.

## How to maintain it

**5–10 items per folder.** Split into subfolders when a folder exceeds this.

**Keep descriptions current.** After any change, rewrite affected descriptions.

**Before ending a session**, save what you learned:

1. Capture — write new knowledge to context-db. If the next session would need
   it, it belongs here.
2. Summarize — rewrite affected descriptions.
3. Cross-reference — add "See also" links if the topic spans folders.
4. Reorganize — split or merge folders to stay at 5–10 items.
5. Verify — run `context-db-generate-toc.sh` on affected folders.
