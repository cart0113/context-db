# Getting Started

## 1. Copy the scripts

Copy `bin/show_toc.sh` into your project's `bin/` directory and make it
executable. Copy `context-db-instructions.md` into your `context-db/` folder —
this is the single source of truth that tells agents how to read, write, and
maintain context documents.

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

> [!important] `context-db-instructions.md` is the file you copy into each
> project. It contains all the rules — reading via `show_toc.sh`, writing back
> discoveries, and maintaining YAML frontmatter. Your `AGENTS.md` and
> tool-specific config files should point to it rather than restating the rules.
> Re-copy this file periodically from the context-db repo to stay current with
> the latest instructions.

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

The bootstrapping pattern is simple: **point your agent to
`context-db-instructions.md` and let that file do the rest.** Don't restate the
context-db rules in your agent config — just reference the instructions file.

Add a context-db section to `AGENTS.md` (or `.cursorrules`, `AGENTS.md`, etc.):

```markdown
## context-db

Read `context-db/context-db-instructions.md` — it contains all rules for
reading, writing, and maintaining the project knowledge database.
```

For Claude Code, also add `.claude/rules/context-db.md` so the instructions load
automatically at session start:

```markdown
This project uses context-db. Read `context-db/context-db-instructions.md` for
how to navigate the project knowledge database.
```

> [!tip] The `templates/` directory has pre-formatted bootstrap text for Claude
> Code, Codex, and Cursor — each tailored to that tool's conventions. These are
> standalone copies of `context-db-instructions.md` formatted for tools that
> don't support `.claude/rules/`.

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
