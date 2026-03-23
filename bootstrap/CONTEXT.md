## context-md

This project organizes knowledge using [context-md](https://github.com/cart0113/context-md) — hierarchical Markdown files with auto-generated tables of contents for progressive disclosure.

### Structure

Example structure below. All folder and file names are abstract placeholders — they have nothing to do with this project's actual files. Name yours to match your content:

```
CONTEXT/
├── CONTEXT_toc.md                  ← generated — never edit
├── CONTEXT.md                      ← folder description (frontmatter only)
├── main_project_context/
│   ├── main_project_context_toc.md ← generated
│   ├── main_project_context.md     ← folder description
│   ├── topic_a/
│   │   ├── topic_a_toc.md          ← generated
│   │   ├── topic_a.md              ← folder description
│   │   ├── document_1.md           ← document (frontmatter + body)
│   │   └── document_2.md
│   └── topic_b/
│       ├── topic_b_toc.md
│       ├── topic_b.md
│       └── ...
└── standards/
    ├── standards_toc.md
    ├── standards.md
    └── ...
```

Every `.md` file has YAML frontmatter with a `description` — a one-line summary of what it covers. Every folder with a description file gets an auto-generated `_toc.md` listing its contents by description and path.

The `description` is the only thing shown in the TOC. It is how an agent decides whether to read a file without opening it. Write descriptions that make this decision easy.

### Reading

Start at `CONTEXT/CONTEXT_toc.md`. Each TOC entry has a description and a path:

- Path ending in `_toc.md` → subfolder. Read that TOC to go deeper.
- Any other path → document. Read it if the description is relevant to your task.

Only fetch what you need. Use descriptions to skip irrelevant branches entirely.

### Writing

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

**Never edit `_toc.md` files.** They are built automatically from descriptions by `bin/build_toc.sh`.
