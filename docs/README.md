# context-md

A standard for organizing LLM context using modular, auto-discovered Markdown files.

## The Problem

Teams use [SKILL.md](https://github.com/anthropics/skills) for general project context
because it's standard and portable. But skills are designed for *procedures* — filling
them with background knowledge degrades skill performance and conflates "what to do"
with "what to know."

context-md is a dedicated standard for **background knowledge and project context**.

## How It Works

The root `CONTEXT/` directory has a `context.cfg` (plain YAML) and a generated
`context_toc.md`. Each subfolder has `<folder>.md` (human-edited) and
`<folder>_toc.md` (generated).

The LLM reads the `_toc.md` first, sees one-line descriptions of every resource,
and fetches only what's relevant.

## Read More

- [Quick Start](getting-started.md) — step-by-step setup
- [Specification](specification.md) — full format reference
- [Script Reference](script-reference.md) — build_toc.sh and format_md.py
- [Why context-md?](blog/why-context-md.md) — design rationale

## Source

[github.com/cart0113/context-md](https://github.com/cart0113/context-md)
