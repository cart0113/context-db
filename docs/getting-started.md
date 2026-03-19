# Quick Start

## 1. Create a CONTEXT/ directory

```
your_project/
└── CONTEXT/
    ├── CONTEXT.md       ← you write this
    └── CONTEXT_toc.md   ← generated
```

## 2. Write the description file

The description file identifies the folder as a context node. It should only contain YAML front matter with a `description` key:

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

# Architecture

(content)
```

## 4. Build

```bash
bin/build_toc.sh
```

By default, only changed TOC files are rebuilt. Use `--build-all` to force a full rebuild.

## 5. Wire up auto-rebuild

```bash
cp hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

## 6. Wire up the agent entry point

Copy the template for your tool so it reads `CONTEXT/` on startup:

**Claude Code:**
```bash
mkdir -p .claude/rules
cp templates/claude-code.md .claude/rules/context-md.md
```

**Cursor:**
```bash
mkdir -p .cursor/rules
cp templates/cursor-rule.mdc .cursor/rules/context-md.mdc
```

**Codex:**
```bash
cat templates/codex.md >> AGENTS.md
```

Or paste the text from `bootstrap/CONTEXT_MD_SYSTEM_INSTRUCTIONS.md` into any rule file or system prompt.

## Sharing context via symlinks

Any subfolder can be a symlink to a shared resource:

```bash
ln -s /shared/coding_standards CONTEXT/coding_standards
```

The script reads descriptions from symlinked directories but never writes into them.
