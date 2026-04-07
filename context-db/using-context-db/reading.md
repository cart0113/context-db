---
description: How to navigate and read the context-db using show_toc.sh
---

## Navigating

Run `show_toc.sh` on any folder to see its table of contents:

```
show_toc.sh context-db/
show_toc.sh context-db/some-folder/
```

The output lists subfolders and files with their descriptions. Use descriptions
to decide relevance before opening a file. Only fetch what you need — the tree
is designed so you can find what you need in two or three hops.

## Output format

```
## Subfolders
- description: ...
  path: subfolder/

## Files
- description: ...
  path: filename.md
```

Subfolder paths end with `/` — run `show_toc.sh` on them to go deeper. File
paths are relative to the folder you scanned.

## Principles

- **Read logarithmically.** Each folder level should halve the search space.
  Scan the TOC, pick the relevant branch, go deeper.
- **Trust descriptions.** If a description says a file isn't relevant, skip it.
  Descriptions are maintained to be accurate summaries.
- **Don't read everything.** The system is designed for selective access.
  Reading the entire database defeats the purpose.
