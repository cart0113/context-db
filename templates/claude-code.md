---
description: Discover and maintain project context via context-db TOC files
---

`context-db/` is this project's **context knowledge database** — hierarchical Markdown files with auto-generated tables of contents, managed by [context-db](https://github.com/cart0113/context-db).

## Structure

Example structure below. All folder and file names are abstract placeholders — name yours to match your content:

```
context-db/
├── context-db-instructions.md      ← how to use the context-db
├── context-db-toc.md               ← generated — never edit
├── my-project/
│   ├── my-project.md               ← folder description
│   ├── my-project-toc.md           ← generated
│   ├── topic-a/
│   │   ├── topic-a.md              ← folder description
│   │   ├── topic-a-toc.md          ← generated
│   │   ├── document-1.md           ← document (frontmatter + body)
│   │   └── document-2.md
│   └── topic-b/
│       ├── topic-b.md
│       ├── topic-b-toc.md
│       └── ...
└── standards/
    ├── standards.md
    ├── standards-toc.md
    └── ...
```

Every `.md` file has YAML frontmatter with a `description` — a one-line summary of what it covers. Every folder with a description file gets an auto-generated `-toc.md` listing its contents by description and path.

The `description` is the only thing shown in the TOC. It is how an agent decides whether to read a file without opening it. Write descriptions that make this decision easy.

## Reading

Start at `context-db/context-db-toc.md`. Each TOC entry has a description and a path:

- Path ending in `-toc.md` → subfolder. Read that TOC to go deeper.
- Any other path → document. Read it if the description is relevant to your task.

Only fetch what you need. Use descriptions to skip irrelevant branches entirely.

## Writing

There are two kinds of `.md` files in the context tree:

**Documents** — frontmatter plus a markdown body. When you create or edit a document, keep its `description` accurate so future reads are correctly filtered.

```yaml
---
description: What this covers and why you'd read it
---

# Title

(content)
```

**Folder descriptions** — `<foldername>.md` with frontmatter only, no body. These register the folder as a context node so it appears in the parent TOC.

```yaml
---
description: What this folder covers
---
```

**Never edit `-toc.md` files.** They are built automatically from descriptions by `bin/build_toc.sh`.
