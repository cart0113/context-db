# Context-MD System

This project uses the **context-md** standard for organizing LLM context.

## Read This Once

This file (`CONTEXT/SYSTEM.md`) explains how the context system works. You only need to read it once per session. If you encounter another project that also uses context-md and has its own `CONTEXT/SYSTEM.md`, you do not need to read it again — the system works the same way everywhere.

## How the System Works

```
project/
└── CONTEXT/
    ├── SYSTEM.md           ← this file (read once, not listed in any TOC)
    ├── CONTEXT_TOC.md      ← your entry point; start here for context
    ├── doc1.md             ← context document
    ├── doc2.md
    └── SUBTOPIC/
        ├── CONTEXT_TOC.md  ← entry point for this subtopic
        └── detail.md
```

## Using Context Efficiently

1. **Start with `CONTEXT/CONTEXT_TOC.md`** — it lists all available context with one-line descriptions.
2. **Read descriptions first** — use them to decide which files are relevant to your current task.
3. **Fetch only what you need** — do not load all context upfront.
4. **For subfolders**, read that folder's `CONTEXT_TOC.md` before diving into individual files.
5. **Eager-read folders** — if a TOC's config marks a folder as `eager_read`, load it automatically.

## TOC Structure

Each `CONTEXT_TOC.md` contains:

- **Front matter** — `title` and `description` identifying the scope of this context node
- **Instructions section** — project-specific guidance for AI assistants
- **Config section** — controls discovery depth, ignore patterns, eager-read overrides
- **Subfolders table** — auto-generated list of subdirectory context nodes
- **Files table** — auto-generated list of context documents in this directory

The tables are rebuilt automatically by `bin/build_toc.sh` from the front matter of each resource. You do not need to maintain them manually.

## Key Principle

Context-md is built around *progressive discovery*: you should always know what context *exists* (via the TOC) before deciding what to *read*. This keeps token usage low and keeps your focus on the task at hand.
