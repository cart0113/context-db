# Specification

## File Layout

A context hierarchy starts with a root directory containing `context.cfg`:

```
CONTEXT/
├── context.cfg              (required)  root config — plain YAML
├── context_toc.md           (generated) discovery index
├── my_project/
│   ├── my_project.md        (required)  subfolder description
│   ├── my_project_toc.md    (generated) subfolder index
│   ├── architecture.md      (optional)  context document
│   └── CODING/
│       ├── CODING.md
│       ├── CODING_toc.md
│       └── defensive.md
```

## Root config: context.cfg

Plain YAML file with at minimum a `description`:

```yaml
description: One-line summary (appears as the root TOC description)
```

Optional config fields:

```yaml
description: Payments service context
ignore: [scratch, old_docs]
follow_symlinks: [CODING]
```

| Field | Default | Description |
|-------|---------|-------------|
| `description` | *(required)* | Summary shown in the root `context_toc.md` |
| `ignore` | `[]` | Names to exclude from the TOC and skip during walk |
| `follow_symlinks` | `[]` | Symlinked folders to recurse into |

## Subfolder description: `<folder>.md`

Contains a fenced YAML `description` block, optionally followed by prose:

~~~markdown
```yaml description
description: One-line summary (appears in parent's TOC)
```

Optional prose guidance for LLMs.
~~~

| Field | Type | Description |
|-------|------|-------------|
| `description` | string | Summary shown in parent's Subfolders table |

An optional `config` block controls walk behavior for that subfolder:

~~~markdown
```yaml config
ignore: [scratch]
follow_symlinks: [CODING]
```
~~~

## Context Documents

Standard `.md` files with YAML front matter:

```markdown
---
description: One-line summary for the TOC
---

Content...
```

## Discovery Rules

When building a TOC, the script scans:

**Subfolders** — immediate subdirectories containing `<subfoldername>.md`.

**Files** — `.md` files in the directory, excluding `<folder>.md`,
`<folder>_toc.md`, `context_toc.md`, and anything in the ignore list or
underscore/dot-prefixed.

## Symlinks

Symlinked directories are read (to get descriptions) but never written to.
They are automatically marked *(read-only)* in the TOC. Use `follow_symlinks`
in the parent's config to recurse into a symlinked directory.

## Change Detection

`build_toc.sh --check` only rebuilds a TOC when any of these are newer:
- The `context.cfg` or `<folder>.md` file
- Any `.md` file in the directory
- Any `<subfolder>.md` in a subdirectory
