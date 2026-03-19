# Quick Start

## 1. Create a CONTEXT/ directory

```
your_project/
└── CONTEXT/
    ├── CONTEXT.md       ← you write this
    └── CONTEXT_toc.md   ← generated
```

## 2. Write the description file

```markdown
---
description: My project — architecture and coding conventions
---
```

## 3. Add context documents

```markdown
---
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

## 6. Wire up the agent entry point

**Skill** (Claude Code, Codex):
```bash
ln -s /path/to/context-md/bootstrap/skill.md your_project/skills/context-md.md
```

**Cursor rule:**
```bash
cp /path/to/context-md/templates/cursor-rule.mdc .cursor/rules/context-md.mdc
```

## Sharing context via symlinks

Any subfolder can be a symlink to a shared resource:

```bash
ln -s /shared/coding-standards CONTEXT/coding_standards
```

Symlinked directories appear as *(read-only)* in the TOC. The script never writes into them.
