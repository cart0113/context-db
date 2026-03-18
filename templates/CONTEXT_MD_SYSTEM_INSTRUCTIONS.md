# Context Instructions

## How This System Works

This project uses **context-md** to organize background knowledge for AI assistants.

```
CONTEXT/
├── CONTEXT_MD_SYSTEM_INSTRUCTIONS.md  ← this file (entry point, read first)
├── CONTEXT_TOC.md                     ← auto-generated discovery index
├── CONTEXT.yml                        ← config (not for LLM consumption)
└── *.md                               ← context documents
```

**Read this file once per session.** If you encounter another project that also uses
context-md, you do not need to read its system instructions again — the system works
the same way everywhere.

### Using Context Efficiently

After reading this file:

1. **Read `CONTEXT/CONTEXT_TOC.md`** — the full index of available context with
   one-line descriptions for every subfolder and file.
2. **Scan descriptions** — identify which resources are relevant to your current task.
3. **Fetch only what you need** — do not load all context upfront.
4. **For subfolders**, read that folder's `CONTEXT_TOC.md` before its individual files.
5. **Eager-read folders** — if the TOC lists an "Always Load" section, load those
   folders immediately.

---

## About This Project

<!-- Replace this section with project-specific guidance -->

Describe what this project is and any guidance specific to this codebase.

For example:
- What the project does and its main components
- Which context subfolder to load for what kind of work
- Key design decisions or constraints to keep in mind
- Anything that is easy to get wrong without context
