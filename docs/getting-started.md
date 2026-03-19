# Quick Start

## 1. Create a CONTEXT/ directory with context.cfg

```
your_project/
└── CONTEXT/
    ├── context.cfg        ← you write this (plain YAML)
    └── context_toc.md     ← generated
```

## 2. Write context.cfg

```yaml
description: Payments service — architecture and coding conventions
```

Optional config fields:

```yaml
description: Payments service — architecture and coding conventions
ignore: [scratch]
follow_symlinks: [CODING]
```

## 3. Add context subfolders

Create a subfolder with a `<folder>.md` description file:

~~~markdown
```yaml description
description: System architecture and data flow
```
~~~

## 4. Add context documents

Individual `.md` files use standard YAML front matter:

```markdown
---
description: System components and data flow
---

(content)
```

## 5. Build

```bash
bin/build_toc.sh CONTEXT/
```

## 6. Wire up auto-rebuild

```bash
cp hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

The hook uses `--check` mode — TOCs are only rebuilt when source files change.

## 7. Wire up the agent entry point

**Skill** (Claude Code, Codex):
```bash
ln -s /path/to/context-md/bootstrap/skill.md your_project/skills/context-md.md
```

**Cursor rule:**
```bash
mkdir -p .cursor/rules
cp /path/to/context-md/templates/cursor-rule.mdc .cursor/rules/context-md.mdc
```

## Sharing context via symlinks

Any subfolder can be a symlink to an external shared resource:

```bash
ln -s /shared/coding-standards CONTEXT/CODING
```

Symlinked directories are automatically marked *(read-only)* in the TOC.
`build_toc.sh` never writes into symlinked directories.
