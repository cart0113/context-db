# Installing context-db

## Quick start

Copy the `bootstrap/` folder contents into your project root:

```bash
cp -r bootstrap/bin your-project/bin
cp -r bootstrap/context-db your-project/context-db
chmod +x your-project/bin/show_toc.sh
```

This gives you:

```
your-project/
├── bin/
│   └── show_toc.sh
└── context-db/
    └── context-db-instructions.md
```

## Create your project folder

The canonical structure uses a `<project>-project/` folder for core project
knowledge:

```
context-db/
├── context-db-instructions.md
└── acme-payments-project/
    └── acme-payments-project.md      ← folder description
```

Create the folder and its description file:

```bash
mkdir context-db/acme-payments-project
```

```yaml
# context-db/acme-payments-project/acme-payments-project.md
---
description: Acme Payments — architecture, APIs, and data model
---
```

The description file has frontmatter only, no body. It registers the folder as a
context node in the TOC.

Add context documents alongside it:

```
context-db/
├── context-db-instructions.md
└── acme-payments-project/
    ├── acme-payments-project.md
    ├── architecture.md
    └── data-model/
        ├── data-model.md
        └── entities.md
```

## Add ancillary folders

Zero or more ancillary folders sit alongside the main project folder — coding
standards, writing guides, domain glossaries, etc. These can be committed
directly or symlinked from other repos:

```
context-db/
├── context-db-instructions.md
├── acme-payments-project/            ← main project context
├── coding-standards/                 ← symlinked from shared repo
└── git-standards/                    ← symlinked from shared repo
```

See [Cross-Project Sharing](../guide/cross-project-sharing.md) for symlink
patterns.

## Bootstrap your agent

Point your agent config at `context-db-instructions.md` — that file contains all
the rules. Don't restate them.

**AGENTS.md** (or equivalent):

```markdown
## context-db

Read `context-db/context-db-instructions.md` — it contains all rules for
reading, writing, and maintaining the project knowledge database.
```

**Claude Code** — also add `.claude/rules/context-db.md`:

```markdown
This project uses context-db. Read `context-db/context-db-instructions.md` for
how to navigate the project knowledge database.
```

The `templates/` directory in the context-db repo has pre-formatted bootstrap
text for Claude Code, Codex, and Cursor.

## Verify

```bash
bin/show_toc.sh context-db/
```

You should see your project folder listed with its description.

## Optional: pre-commit hook

```bash
cp hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

Formats staged markdown (prettier) and Python (ruff) on commit.
