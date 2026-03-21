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

## 6. Bootstrap the agent

The agent needs instructions on how context-md works. The `bootstrap/` folder has a reference document; `templates/` has ready-made wrappers for common tools.

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

Or paste the text from `bootstrap/CONTEXT_MD_SYSTEM_INSTRUCTIONS.md` into any rule file or system prompt. These are reference documents — the exact delivery mechanism depends on your setup.

## Sharing and wiring up context

context-md doesn't prescribe where context lives. A few patterns:

```bash
# Symlink shared context into your project
ln -s /shared/coding_standards CONTEXT/coding_standards

# Point rules at context outside the project
# (in CLAUDE.md, .cursorrules, or AGENTS.md)
# Read ~/team/CONTEXT/CONTEXT_toc.md for team standards.

# Reference a specific subfolder instead of the whole tree
# Read CONTEXT/acme_payments/acme_payments_toc.md to start.
```

The build script reads descriptions from symlinked directories but never writes into them.
