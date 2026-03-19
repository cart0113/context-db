# context-md System

This project organizes background knowledge for AI assistants using **context-md**.

## How It Works

```
CONTEXT/
├── context.cfg             ← root config (plain YAML)
├── context_toc.md          ← auto-generated index (never edit)
└── subtopic/
    ├── subtopic.md         ← describes this subfolder
    ├── subtopic_toc.md     ← auto-generated index
    └── detail.md           ← context document
```

## How to Use It

1. **Read `CONTEXT/context_toc.md`** for a one-line description of every available
   resource (subfolders and files).
2. **Scan descriptions** to decide what is relevant to the current task.
3. **Fetch only what you need** — do not load everything.
4. **For subfolders**, read that folder's `*_toc.md` before individual files.

## File Conventions

| File | Purpose |
|------|---------|
| `context.cfg` | Root config — plain YAML with `description` and optional walk config |
| `<folder>.md` | Human-edited description for a subfolder (fenced YAML block) |
| `<folder>_toc.md` | Auto-generated discovery index — never edit |
| `*.md` (other) | Context documents with YAML front matter (`description`) |

Read this explanation once. The system works the same way in every project that uses it.
