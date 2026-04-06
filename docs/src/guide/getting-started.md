# Getting Started

## 1. Copy the scripts

Copy `bin/show_toc.sh` into your project's `bin/` directory and make it
executable. Copy `context-db-instructions.md` into your `context-db/` folder —
this file tells agents how to read and write context documents.

```
your-project/
├── AGENTS.md
├── bin/show_toc.sh
└── context-db/
    └── context-db-instructions.md
```

```bash
chmod +x bin/show_toc.sh
```

## 2. Create a project subfolder

Create a folder named after your project. Inside it, create a description file
(`<folder>.md`) with YAML frontmatter containing a one-line `description`. The
description file has frontmatter only — no body content.

```
context-db/
└── my-project/
    └── my-project.md
```

```yaml
---
description: My project — architecture, APIs, and data model
---
```

This marks the folder as a context node. `show_toc.sh` uses the description to
build the TOC entry.

## 3. Add context documents

Each document has YAML frontmatter with a `description` (this is what appears in
the TOC) and markdown content below.

```
context-db/
└── my-project/
    ├── my-project.md
    ├── architecture.md
    └── data-model.md
```

```yaml
---
description: System components, data flow, and service boundaries
---
# Architecture

The system consists of three services...
```

The `description` is the most important part — it's the only thing agents see
when browsing the TOC. Write the most useful, specific summary possible.

## 4. Verify

Run `show_toc.sh` on the root `context-db/` folder to see the top-level TOC:

```bash
bin/show_toc.sh context-db/
```

```
## Subfolders

- description: My project — architecture, APIs, and data model
  path: my-project/my-project-toc.md
```

Run it on the subfolder to see its documents:

```bash
bin/show_toc.sh context-db/my-project/
```

```
## Files

- description: System components, data flow, and service boundaries
  path: architecture.md
- description: Database schema, entities, and relationships
  path: data-model.md
```

## 5. Bootstrap your agent

Point your agent's entry file to the knowledge database. Add a context-db
section to `AGENTS.md` (or `.cursorrules`, `AGENTS.md`, etc.):

```markdown
## context-db

Read `context-db/context-db-instructions.md` for the project knowledge database.
```

The `templates/` directory has pre-formatted bootstrap text for Claude Code,
Codex, and Cursor — each tailored to that tool's conventions.

For Claude Code, you can also add a `.claude/rules/context-db.md` file:

```markdown
This project uses context-db. Read `context-db/context-db-instructions.md` for
how to navigate the project knowledge database.
```

## 6. Optional: pre-commit hook

Install the pre-commit hook for auto-formatting staged files (prettier for
markdown, ruff for Python):

```bash
cp hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

## Next steps

- [Cross-Project Sharing](cross-project-sharing.md) — symlink context from other
  repos, share standards across projects
- [Reference](../reference/specification.md) — full format specification
