# Specification

## File Layout

A context node is any directory containing `<foldername>.md`:

```
CONTEXT/
├── CONTEXT.md           (required)  human-edited description and config
├── CONTEXT_toc.md       (generated) discovery index
├── architecture.md      (optional)  context document
└── CODING/
    ├── CODING.md
    ├── CODING_toc.md
    └── defensive.md
```

## `<folder>.md` Format

Contains one or two fenced YAML blocks, optionally followed by prose:

~~~markdown
```yaml description
title: Human-readable name
description: One-line summary (appears in parent's TOC)
```

```yaml config
skip_underscore: true
ignore: [scratch]
read_only: [CODING]
eager_read: [CODING]
```

Optional prose guidance for LLMs.
~~~

### Description block (required)

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Heading in the generated `_toc.md` |
| `description` | string | Summary shown in parent's Subfolders table |

### Config block (optional)

| Field | Default | Description |
|-------|---------|-------------|
| `skip_underscore` | `true` | Skip files/folders starting with `_` |
| `ignore` | `[]` | Names to exclude from the TOC |
| `read_only` | `[]` | Include in TOC but don't rebuild |
| `eager_read` | `[]` | Folders the LLM should always load |

## Context Documents

Standard `.md` files with YAML front matter:

```markdown
---
title: Document Title
description: One-line summary for the TOC
---

Content...
```

## Discovery Rules

When building a `<folder>_toc.md`, the script scans:

**Subfolders** — immediate subdirectories containing `<subfoldername>.md`.

**Files** — `.md` files in the directory, excluding `<folder>.md`,
`<folder>_toc.md`, and anything in the ignore list or underscore-prefixed.

## Symlinks

Symlinked directories are read (to get descriptions) but never written to.
They are automatically marked *(read-only)* in the TOC. The `read_only` config
list can also mark non-symlinked directories.

## Change Detection

`build_toc.sh --check` only rebuilds a `_toc.md` when any of these are newer:
- The `<folder>.md` file
- Any `.md` file in the directory
- Any `<subfolder>.md` in a non-symlinked subdirectory
