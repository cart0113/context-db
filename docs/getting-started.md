# Quick Start

## 1. Create a CONTEXT/ directory

```
your_project/
└── CONTEXT/
    ├── CONTEXT.md       ← you write this
    └── CONTEXT_toc.md   ← generated
```

## 2. Write CONTEXT.md

~~~markdown
```yaml description
title: My Project
description: Payments service — architecture and coding conventions
```

Load CODING/ when writing or reviewing code.
~~~

The `description` block is required. A `config` block is optional:

~~~markdown
```yaml config
read_only: [CODING]
ignore: [scratch]
```
~~~

## 3. Add context documents

```markdown
---
title: Architecture Overview
description: System components and data flow
---

(content)
```

## 4. Build

```bash
bin/build_toc.sh CONTEXT/
```

## 5. Wire up auto-rebuild

```bash
cp hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

The hook uses `--check` mode — TOCs are only rebuilt when source files change.

## 6. Wire up the agent entry point

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
