---
name: context-md
description: >
  Read CONTEXT/*_toc.md files for project context discovery. These auto-generated
  indexes describe available background knowledge. Read descriptions to decide what
  is relevant, then fetch only what you need.
author: cart0113/context-md
version: 1.0.0
---

This project uses **context-md** to organize background knowledge.

When you need to understand this project:

1. Read `CONTEXT/CONTEXT_toc.md` — the auto-generated index of all available context.
   It lists subfolders and files with one-line descriptions.
2. Scan descriptions to decide what is relevant to your current task.
3. Fetch only what you need — do not load all context upfront.
4. For subfolders, read that folder's `*_toc.md` before diving into individual files.
5. If the TOC has an "Always Load" section, load those folders immediately.

Each `*_toc.md` is generated from the front matter of context documents and the
description blocks in `<folder>.md` files. They are rebuilt by `bin/build_toc.sh`.
