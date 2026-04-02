## context-md

`CONTEXT/` is this project's **context knowledge database** — hierarchical Markdown files with auto-generated tables of contents, managed by [context-md](https://github.com/cart0113/context-md).

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

### Maintaining the context knowledge database

The context knowledge database is a living knowledge base, not a snapshot. It should reflect the current state of the project. Stale context is worse than missing context — an agent will act on outdated information with confidence.

**Suggest updates** when you discover something a future agent would need to work safely on this codebase — architecture decisions, non-obvious patterns, constraints, gotchas, data model relationships. The heuristic: if you had to figure it out the hard way, it belongs in the context knowledge database. Ask before writing.

**Flag stale content** when you read a context document that contradicts the current code, describes something that no longer exists, or would lead an agent to a wrong decision. Remove or correct it.

**Suggest reorganization** when a document covers multiple distinct topics or a folder's TOC has grown past a quick scan. Moving content into a subfolder automatically creates a new TOC node — a new level of progressive disclosure. This isn't tidying; it directly improves how well a future agent can filter what it reads.

**After any change** to context files:
1. Make sure the `description` in its frontmatter still matches the content.
2. If you created a new folder, add the `<foldername>.md` description file.
3. If a document was deleted or moved, update any references to it in other documents.
