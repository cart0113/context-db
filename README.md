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
│   ├── SYSTEM.md              ← one-time system explanation (never in TOC)
│   ├── CONTEXT_TOC.md         ← entry point: discoverable index of all context
│   ├── project_overview.md
│   ├── architecture.md
│   └── CODING_STYLE/
│       ├── CONTEXT_TOC.md
│       └── defensive_coding.md
└── payments_module/
    └── CONTEXT/
        └── CONTEXT_TOC.md
```

`CONTEXT_TOC.md` is a lightweight index — front matter descriptions from every `.md` file and subfolder are collected into tables. An LLM reads the TOC to understand what context exists, then fetches only what it needs.

## Key Features

- **Progressive discovery** — LLMs read a single TOC first; full documents are fetched only when relevant
- **Modular** — any `CONTEXT/` subtree can be a symlink to a shared resource from another repo
- **Auto-generated TOC** — `bin/build_toc.sh` rebuilds TOC tables from front matter; no manual maintenance
- **Config-driven** — each TOC controls depth, ignore lists, and eager-read overrides
- **Portable** — pure bash (3.2+) script; works on any Unix system with no extra dependencies

## Quick Start

```bash
# 1. Copy the template into your project
cp -r examples/my_project/CONTEXT your_project/CONTEXT

# 2. Edit CONTEXT/CONTEXT_TOC.md front matter and instructions section

# 3. Add .md files with front matter to CONTEXT/

# 4. Build the TOC
bin/build_toc.sh your_project/CONTEXT/

# 5. Optional: wire up the git pre-commit hook
cp hooks/pre-commit your_project/.git/hooks/pre-commit
chmod +x your_project/.git/hooks/pre-commit
```

## CONTEXT_TOC.md Format

```markdown
---
title: My Project Context
description: Context for the payments service — architecture and coding conventions
---

## Instructions for AI Assistants

...your custom instructions...

## Configuration
<!-- CONTEXT_CONFIG
depth: 1
skip_underscore: true
ignore: scratch, old_docs
eager_read: CODING_STYLE
-->

## Subfolders
<!-- CONTEXT_FOLDERS:START -->
<!-- CONTEXT_FOLDERS:END -->

## Files
<!-- CONTEXT_FILES:START -->
<!-- CONTEXT_FILES:END -->
```

The `CONTEXT_FOLDERS` and `CONTEXT_FILES` sections are auto-generated from the `title` and `description` fields in each resource's front matter.

## Documentation

Full documentation, specification, and a blog post explaining the rationale are available at [cart0113.github.io/context-md](https://cart0113.github.io/context-md).

## Tools

| Script | Description |
|--------|-------------|
| `bin/build_toc.sh` | Rebuilds auto-generated TOC sections; run from project root or pass a specific path |
| `bin/format_md.py` | Formats markdown tables to fixed-width alignment |
| `hooks/pre-commit` | Example git pre-commit hook that runs `build_toc.sh` automatically |

## License

MIT
