# Getting Started

## 1. Create context-db/

```
your-project/
├── AGENTS.md
└── context-db/
    ├── context-db-instructions.md
    └── context-db-toc.md            ← generated
```

Copy `context-db-instructions.md` from this repo's `context-db/` folder. This
file tells agents how to read and write context documents.

## 2. Add a project subfolder

Create a folder with a description file. The file has YAML frontmatter only — no
body content.

```
context-db/
└── my-project/
    └── my-project.md
```

```yaml
---
description: My project — architecture and coding conventions
---
```

## 3. Add context documents

Each document has frontmatter with a `description` (appears in the parent TOC)
and content below.

```
context-db/
└── my-project/
    ├── my-project.md
    ├── architecture.md
    └── data-model.md
```

```yaml
---
description: System components and data flow
---
# Architecture

(content)
```

## 4. Build TOCs

```bash
bin/build_toc.sh
```

This generates `my-project-toc.md` and `context-db-toc.md`:

```
context-db/
├── context-db-instructions.md
├── context-db-toc.md               ← generated
└── my-project/
    ├── my-project.md
    ├── my-project-toc.md            ← generated
    ├── architecture.md
    └── data-model.md
```

## 5. Wire up auto-rebuild

Install the pre-commit hook so TOCs rebuild on every commit:

```bash
cp hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

## 6. Bootstrap

Point your agent's entry file to the knowledge database. In `AGENTS.md`:

```markdown
## context-db

Read `context-db/context-db-instructions.md` for the project knowledge database.
```

The `templates/` directory has pre-formatted bootstrap text for Claude Code,
Codex, and Cursor.
