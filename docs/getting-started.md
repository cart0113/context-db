# Quick Start

## 1. Create context-db/

```
your-project/
├── AGENT.md
└── context-db/
    ├── context-db-instructions.md
    └── context-db-toc.md            ← generated
```

Copy `context-db-instructions.md` from this repo's `context-db/` folder.

## 2. Add a project subfolder

Create `context-db/my-project/my-project.md` with frontmatter only:

```yaml
---
description: My project — architecture and coding conventions
---
```

## 3. Add context documents

```yaml
---
description: System components and data flow
---

# Architecture

(content)
```

## 4. Build

```bash
bin/build_toc.sh
```

## 5. Wire up auto-rebuild

```bash
cp hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

## 6. Bootstrap

In your project's `AGENT.md`:

```markdown
## context-db

Read `context-db/context-db-instructions.md` for the project knowledge database.
```

The `templates/` directory has pre-formatted versions for other tools (Cursor, Codex).
