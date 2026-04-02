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

The hook targets `CONTEXT/` by default. Edit the path inside the hook if your context tree lives elsewhere.

## 6. Bootstrap the agent

The agent needs to know how to navigate and maintain the context knowledge database. Paste the bootstrap text into whatever file your agent reads on startup — `AGENT.md`, `CLAUDE.md`, `AGENTS.md`, `.cursorrules`, `.claude/rules/`, a system prompt, or any other mechanism. It can be inline or in a separate file that your startup file references.

The `bootstrap/` directory has reference texts to start from:

- [`bootstrap/CONTEXT.md`](bootstrap/CONTEXT.md) — core instructions: structure, reading, writing.
- [`bootstrap/CONTEXT-extended.md`](bootstrap/CONTEXT-extended.md) — adds proactive maintenance behaviors.

The `templates/` directory has pre-formatted versions for specific tools.

The bootstrap text names `CONTEXT/` as a "context knowledge database." Once your agent has read it, you can say things like "update the context knowledge database" or "add this to the context db" and the agent will know what you mean.

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
