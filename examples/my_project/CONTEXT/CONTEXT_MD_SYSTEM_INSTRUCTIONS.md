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
context-md, you do not need to read its system instructions again.

After reading this file, read `CONTEXT/CONTEXT_TOC.md` to discover available context.
Fetch only what is relevant to your current task.

---

## About This Project

`my_project` is a demo project used to illustrate how context-md works in practice.

- Load `CODING_STYLE/` whenever you are writing or reviewing code
- For API-related work, also load `../api_module/CONTEXT/`
- Domain models are plain data classes — no framework dependencies
