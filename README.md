# context-db

Hierarchical Markdown knowledge base with on-demand tables of contents for LLM
agents.

## How it works

```
your-project/
├── AGENTS.md                         ← "read context-db/context-db-instructions.md"
├── bin/show_toc.sh                   ← TOC generator (prints to stdout)
└── context-db/
    ├── context-db-instructions.md   ← teaches the agent to navigate the tree
    ├── my-project/
    │   ├── my-project.md            ← folder description (frontmatter only)
    │   ├── architecture.md          ← document (frontmatter + body)
    │   └── data-model/
    │       ├── data-model.md
    │       └── entities.md
    └── coding-standards/            ← can be a symlink to shared context
        ├── coding-standards.md
        └── naming-conventions.md
```

`AGENTS.md` bootstraps the agent into `context-db/`. The instructions file
teaches navigation. The agent runs `bin/show_toc.sh` on folders, uses
descriptions to decide relevance, and only fetches what it needs.

## Quick start

1. Create `context-db/` and copy `context-db-instructions.md` into it
2. Copy `bin/show_toc.sh` into your project's `bin/` directory
3. Add your project subfolder with a `<foldername>.md` description file
4. Add context documents with `description:` frontmatter
5. Point `AGENTS.md` to read `context-db/context-db-instructions.md`

## Cross-project sharing

Symlink a published knowledge folder into `context-db/` and `show_toc.sh` picks
it up automatically:

```
context-db/
├── my-project/
│   ├── my-project.md
│   └── architecture.md
└── coding-standards/ → /shared/coding-standards   ← symlink
    ├── coding-standards.md
    └── naming-conventions.md
```

Add symlinked folders to `.gitignore` for private-only context, or commit them
for the whole team. See the cross-project sharing docs for git-sync and git
submodule patterns.

## File format

Every `.md` file has YAML frontmatter with a `description` key. This is the only
thing shown in the TOC — it's how the agent decides whether to read a file.

**Folder description** (`my-project.md`) — frontmatter only, registers the
folder:

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

1. A folder is a context node if it contains `<folder_name>.md`,
   `<folder_name>-instructions.md`, or one of `AGENTS.md`, `CONTEXT.md`,
   `SKILL.md`, `AGENTS.md`
2. `bin/show_toc.sh <folder>` generates a TOC on stdout for that folder
3. Underscore-prefixed and dot-prefixed names are skipped
4. Symlinked folders appear in the TOC and are followed for reading

## Usage

```bash
bin/show_toc.sh context-db/                     # top-level TOC
bin/show_toc.sh context-db/my-project/          # subfolder TOC
bin/show_toc.sh context-db/my-project/data-model/  # deeper
```

## License

MIT
