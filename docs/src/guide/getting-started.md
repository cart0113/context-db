# Getting Started

## 1. Create context-db/

```
your-project/
├── AGENTS.md
├── bin/show_toc.sh
└── context-db/
    └── context-db-instructions.md
```

Copy `context-db-instructions.md` from this repo's `context-db/` folder. This
file tells agents how to read and write context documents.

Copy `bin/show_toc.sh` into your project's `bin/` directory and make it
executable (`chmod +x bin/show_toc.sh`).

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

Each document has frontmatter with a `description` (appears in the TOC) and
content below.

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

## 4. Verify

```bash
bin/show_toc.sh context-db/
```

This prints the TOC to stdout:

```
## Subfolders

- description: My project — architecture and coding conventions
  path: my-project/my-project-toc.md
```

Run it on the subfolder to see its contents:

```bash
bin/show_toc.sh context-db/my-project/
```

## 5. Bootstrap

Point your agent's entry file to the knowledge database. In `AGENTS.md`:

```markdown
## context-db

Read `context-db/context-db-instructions.md` for the project knowledge database.
```

The `templates/` directory has pre-formatted bootstrap text for Claude Code,
Codex, and Cursor.

## 6. Optional: pre-commit hook

Install the pre-commit hook for auto-formatting staged files:

```bash
cp hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```
