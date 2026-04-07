# Getting Started

## 1. Copy the template files

Copy `templates/bin/` and `templates/context-db/` into your project:

```bash
cp -r templates/bin your-project/bin
cp -r templates/context-db your-project/context-db
chmod +x your-project/bin/show_toc.sh
```

## 2. Create your project folder

The main project folder is named `<project>-project/`. Create it with a
description file (frontmatter only, no body):

```
context-db/
└── acme-payments-project/
    └── acme-payments-project.md
```

```yaml
---
description: Acme Payments — architecture, APIs, and data model
---
```

Add context documents alongside it. Each has `description` frontmatter and
markdown content.

## 3. Point your agent at the instructions

Add to `AGENTS.md` (a sample is in `templates/AGENTS.md`):

```markdown
## context-db

Read `context-db/context-db-instructions.md` — it contains all rules for
reading, writing, and maintaining the project knowledge database.
```

For Claude Code, also add `.claude/rules/context-db.md`:

```markdown
This project uses context-db. Read `context-db/context-db-instructions.md` for
how to navigate the project knowledge database.
```

A sample `SKILLS.md` for Claude Code is in `templates/skills/context-db/`.

## 4. Verify

```bash
bin/show_toc.sh context-db/
```

## Next steps

- [Cross-Project Sharing](cross-project-sharing.md) — symlink context from other
  repos
- [Reference](../reference/specification.md) — format specification
