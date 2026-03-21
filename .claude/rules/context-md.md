---
description: Discover and maintain project context via context-md TOC files
---

This project uses context-md to organize background knowledge in `CONTEXT/`.

## Reading

Read `CONTEXT/CONTEXT_toc.md` to start. Each entry has a description and a path.
Use descriptions to decide relevance — skip what you don't need.

- If the path ends in `_toc.md`, it's a subfolder — read that TOC and repeat.
- Otherwise, read the document.

## Writing

When creating or updating context documents:

- **New folder**: create `<foldername>.md` with only YAML frontmatter:
  `description: <one-line summary>`. This marks the folder as a context node.
- **New document**: YAML frontmatter with `description`, then markdown content.
- **Descriptions are critical.** The description is the only thing an agent sees in
  the TOC when deciding whether to read a document. Write the most useful, concise
  summary possible — it should tell the reader whether they need this document
  without opening it.
- Run `bin/build_toc.sh` to regenerate TOC files after changes.
