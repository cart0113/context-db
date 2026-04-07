---
description: 'READ THIS FIRST — what context-db is and how to get started'
---

`context-db/` is this project's knowledge database — hierarchical Markdown with
on-demand TOCs via `show_toc.sh`.

## How it works

Every `.md` file has YAML frontmatter with a `description` field — a one-line
summary shown in the TOC. Run `show_toc.sh` on any folder to see its contents
without opening files. Use descriptions to decide what to read. Only fetch what
is relevant to the current task.

Subfolders appear when they contain a `<folder-name>.md` file (frontmatter
only). Navigate deeper by running `show_toc.sh` on subfolders.

## Quick start

1. Run `show_toc.sh context-db/` to see the top-level TOC.
2. Drill into subfolders by running `show_toc.sh` on them.
3. Read files whose descriptions match your current task.
4. After learning something non-obvious, write it back — see `writing.md`.
