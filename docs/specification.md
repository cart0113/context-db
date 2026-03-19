# Specification

## Context Nodes

A context node is any directory containing a recognized description file:
- `<foldername>.md` (preferred)
- `CONTEXT.md`, `SKILL.md`, `AGENT.md`, or `AGENTS.md`

The description file must have YAML front matter with a `description` key:

```markdown
---
description: One-line summary (appears in parent's TOC)
---

Optional prose.
```

## Context Documents

Standard `.md` files with YAML front matter:

```markdown
---
description: One-line summary for the TOC
---

Content...
```

## Discovery Rules

When building a `<folder>_toc.md`, the script scans:

**Subfolders** — immediate subdirectories containing a recognized description file.

**Files** — `.md` files in the directory, excluding the description file, the `_toc.md`, and any underscore/dot-prefixed names.

## Symlinks

Symlinked directories are read (to get descriptions) but never written to. They appear as *(read-only)* in the TOC.

## Change Detection

`build_toc.sh --check` only rebuilds a `_toc.md` when any source file is newer:
- The description file
- Any `.md` file in the directory
- Any description file in a subdirectory
