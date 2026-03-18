# context-md

A standard for organizing LLM context using modular, auto-discovered Markdown files.

## The Problem

As LLM-assisted development has matured, many teams have reached for the [SKILL.md](https://github.com/anthropics/skills) format to share background knowledge and project context — not just procedures. Skills are excellent for what they were designed to do, but using them as a general knowledge store has downsides: skill subsystems are bounded in how many they can load, filling that space with raw context degrades procedural skill performance, and the format conflates *what to do* with *what to know*.

`context-md` solves this by providing a dedicated, portable standard for **background knowledge and project context**.

## Core Idea

Every project (or module) that wants to share context with an LLM includes a `CONTEXT/` folder:

```
my_project/
├── CONTEXT/
│   ├── CONTEXT.yml                        ← config: title, description, indexing options
│   ├── CONTEXT_MD_SYSTEM_INSTRUCTIONS.md  ← entry point: system + project guidance
│   ├── CONTEXT_TOC.md                     ← auto-generated discovery index
│   ├── architecture.md                    ← context document
│   └── CODING_STYLE/
│       ├── CONTEXT.yml
│       ├── CONTEXT_TOC.md
│       └── conventions.md
└── payments_module/
    └── CONTEXT/
        ├── CONTEXT.yml
        └── CONTEXT_TOC.md
```

The agent entry point is `CONTEXT_MD_SYSTEM_INSTRUCTIONS.md` — a cursor rule or skill
points the LLM here at session start. That file explains the context-md system and
contains project-specific guidance. It then directs the LLM to `CONTEXT_TOC.md`, the
auto-generated index of every available context resource.

## Key Features

- **Clear entry point** — `CONTEXT_MD_SYSTEM_INSTRUCTIONS.md` is the one file agents are directed to; it explains the system and orients them to the project
- **Progressive discovery** — LLMs read a single TOC first; full documents are fetched only when relevant
- **Modular** — any `CONTEXT/` subtree can be a symlink to a shared resource from another repo
- **Auto-generated TOC** — `bin/build_toc.sh` rebuilds the index from `CONTEXT.yml` configs and file front matter; no manual maintenance
- **Portable** — pure bash (3.2+) script; works on any Unix system with no extra dependencies

## Quick Start

```bash
# 1. Copy the template into your project
cp -r examples/my_project/CONTEXT your_project/CONTEXT

# 2. Edit CONTEXT/CONTEXT.yml (title, description, options)
# 3. Edit CONTEXT/CONTEXT_MD_SYSTEM_INSTRUCTIONS.md (project-specific guidance)
# 4. Add .md files with front matter to CONTEXT/

# 5. Build the TOC
bin/build_toc.sh your_project/CONTEXT/

# 6. Wire up the pre-commit hook
cp hooks/pre-commit your_project/.git/hooks/pre-commit
chmod +x your_project/.git/hooks/pre-commit
```

## CONTEXT.yml Format

```yaml
title: My Project Context
description: Context for the payments service — architecture and coding conventions

depth: 1
skip_underscore: true
ignore: []
read_only: []      # Include in TOC but skip rebuilding (for symlinked external resources)
eager_read: []     # Tell LLM to always load these when reading this TOC
```

## Wiring Up the Entry Point

### As a skill (Claude Code, Codex, etc.)

Symlink `skills/context-md.md` into your project's skills directory:

```bash
ln -s /path/to/context-md/skills/context-md.md your_project/skills/context-md.md
```

### As a Cursor rule

Copy and customize `templates/cursor-rule.mdc` into your project:

```bash
mkdir -p your_project/.cursor/rules
cp /path/to/context-md/templates/cursor-rule.mdc your_project/.cursor/rules/context-md.mdc
```

## Tools

| Script | Description |
|--------|-------------|
| `bin/build_toc.sh` | Rebuilds all `CONTEXT_TOC.md` files; run from project root or pass a specific path |
| `bin/format_md.py` | Formats Markdown tables to fixed-width column alignment |
| `hooks/pre-commit` | Example pre-commit hook that runs `build_toc.sh` automatically |

## Documentation

Full documentation and design rationale at [cart0113.github.io/context-md](https://cart0113.github.io/context-md).

## License

MIT
