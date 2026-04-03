# context-db

Hierarchical Markdown knowledge base with auto-generated tables of contents for LLM agents.

## How it works

```
your-project/
├── AGENTS.md                         ← "read context-db/context-db-instructions.md"
└── context-db/
    ├── context-db-instructions.md   ← teaches the agent to navigate the tree
    ├── context-db-toc.md            ← generated — never edit
    ├── my-project/
    │   ├── my-project.md            ← folder description (frontmatter only)
    │   ├── my-project-toc.md        ← generated
    │   ├── architecture.md          ← document (frontmatter + body)
    │   └── data-model/
    │       ├── data-model.md
    │       ├── data-model-toc.md
    │       └── entities.md
    └── coding-standards/            ← can be a symlink to shared context
        ├── coding-standards.md
        └── naming-conventions.md
```

`AGENTS.md` bootstraps the agent into `context-db/`. The instructions file teaches navigation. The agent reads TOCs, uses descriptions to decide relevance, and only fetches what it needs.

## Quick start

1. Create `context-db/` and copy `context-db-instructions.md` into it
2. Add your project subfolder with a `<foldername>.md` description file
3. Add context documents with `description:` frontmatter
4. Run `bin/build_toc.sh` to generate TOCs
5. Point `AGENTS.md` to read `context-db/context-db-instructions.md`

## File format

Every `.md` file has YAML frontmatter with a `description` key. This is the only thing shown in the TOC — it's how the agent decides whether to read a file.

**Folder description** (`my-project.md`) — frontmatter only, registers the folder:

```yaml
---
description: My project — architecture and data model
---
```

**Document** (`architecture.md`) — frontmatter plus content:

```yaml
---
description: System components, data flow, and service boundaries
---

# Architecture

(content)
```

## Rules

1. A folder is a context node if it contains `<folder_name>.md`, `<folder_name>-instructions.md`, or one of `AGENTS.md`, `CONTEXT.md`, `SKILL.md`, `AGENTS.md`
2. `bin/build_toc.sh` generates `<folder>-toc.md` for each context node
3. Underscore-prefixed and dot-prefixed names are skipped
4. Symlinked folders appear in the TOC but are never written into

## Building

```bash
bin/build_toc.sh                    # rebuild changed TOCs
bin/build_toc.sh --build-all        # force rebuild all
bin/build_toc.sh context-db/        # build specific tree
```

Pre-commit hook: `cp hooks/pre-commit .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit`

## License

MIT
