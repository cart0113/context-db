# context-md

A standard for organizing LLM context using modular, auto-discovered Markdown files.

## The Problem

When working with LLM-assisted development, teams need a reliable way to give models
background knowledge about a project: architecture decisions, coding conventions,
domain concepts, module boundaries. Many have reached for the
[SKILL.md](https://github.com/anthropics/skills) format — it's clean, portable, and
well-supported. But skills are designed for *procedures*, not *knowledge*. Filling the
skill subsystem with raw context degrades procedural skill performance and creates
conceptual confusion between "what to do" and "what to know."

**context-md** is a dedicated standard for background knowledge. It takes the best
ideas from SKILL.md — standardized structure, portability via symlinks, front matter
metadata — and applies them specifically to context organization.

## Core Concept

Every project adds a `CONTEXT/` folder:

```
my_project/
├── CONTEXT/
│   ├── CONTEXT.yml              ← config: title, description, indexing options
│   ├── CONTEXT_INSTRUCTIONS.md  ← prose guidance for LLMs (optional)
│   ├── CONTEXT_TOC.md           ← auto-generated index (never edit by hand)
│   ├── SYSTEM.md                ← one-time system explanation (never indexed)
│   ├── architecture.md          ← context document
│   └── CODING_STYLE/
│       ├── CONTEXT.yml
│       └── CONTEXT_TOC.md
└── payments/
    └── CONTEXT/
        ├── CONTEXT.yml
        └── CONTEXT_TOC.md
```

The LLM reads `CONTEXT_TOC.md` first — a single generated file that indexes everything
available. Based on the task at hand, it fetches only the relevant resources.

## Quick Start

```bash
# Copy the template structure
cp -r examples/my_project/CONTEXT your_project/CONTEXT

# Edit CONTEXT.yml (title, description, options)
# Edit CONTEXT_INSTRUCTIONS.md (LLM guidance)
# Add .md files with YAML front matter

# Build the TOC
bin/build_toc.sh your_project/CONTEXT/

# Wire up auto-rebuild on commit
cp hooks/pre-commit your_project/.git/hooks/pre-commit
chmod +x your_project/.git/hooks/pre-commit
```

## Read More

- [Quick Start](getting-started.md) — step-by-step setup
- [Specification](specification.md) — full format spec
- [TOC Format](toc-format.md) — CONTEXT_TOC.md reference
- [Script Reference](script-reference.md) — build_toc.sh and format_md.py
- [Why context-md?](blog/why-context-md.md) — design rationale and background
