# context-md System

This project organizes background knowledge using **context-md**.

## How to Use

1. **Read `CONTEXT/CONTEXT_toc.md`** — one-line description of every subfolder and file.
2. **Scan descriptions** to decide what is relevant to the current task.
3. **Fetch only what you need** — do not load everything.
4. **For subfolders**, read that folder's `*_toc.md` before individual files.

## File Conventions

| File | Purpose |
|------|---------|
| `<folder>.md` | Description file for a context folder (YAML front matter with `description`) |
| `<folder>_toc.md` | Auto-generated index — never edit |
| `*.md` (other) | Context documents with YAML front matter (`description`) |

Recognized description file names: `<folder_name>.md`, `CONTEXT.md`, `SKILL.md`, `AGENT.md`, `AGENTS.md`.
