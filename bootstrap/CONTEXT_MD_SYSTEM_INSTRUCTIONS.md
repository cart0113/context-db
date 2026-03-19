# context-md System

This project organizes background knowledge for AI assistants using **context-md**.

## How It Works

```
CONTEXT/
├── CONTEXT.md          ← describes this context node (human-edited)
├── CONTEXT_toc.md      ← auto-generated index (never edit)
├── overview.md         ← context documents
└── SUBTOPIC/
    ├── SUBTOPIC.md
    ├── SUBTOPIC_toc.md
    └── detail.md
```

## How to Use It

1. **Read `CONTEXT/<folder>_toc.md`** for a one-line description of every available
   resource (subfolders and files).
2. **Scan descriptions** to decide what is relevant to the current task.
3. **Fetch only what you need** — do not load everything.
4. **For subfolders**, read that folder's `*_toc.md` before individual files.
5. **If a TOC has an "Always Load" section**, load those immediately.

## File Conventions

| File | Purpose |
|------|---------|
| `<folder>.md` | Human-edited description and config for a context folder |
| `<folder>_toc.md` | Auto-generated discovery index — never edit |
| `*.md` (other) | Context documents with YAML front matter (`title`, `description`) |

Read this explanation once. The system works the same way in every project that uses it.
