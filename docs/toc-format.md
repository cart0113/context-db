# TOC File Format

`<folder>_toc.md` files are fully generated. Never edit them.

## Example

```markdown
## Subfolders

- description: Shared coding standards *(read-only)*
  path: coding/coding_toc.md
- description: Schema and migration patterns
  path: database/database_toc.md

## Files

- description: System components and data flow
  path: architecture.md
```

Each entry has `description:` on the first line and `path:` on the second. Symlinked folders are marked *(read-only)*.

## Sections

Sections only appear when there are entries — an empty folder produces an empty TOC.

| Section | Contents |
|---------|----------|
| Subfolders | Subdirectories that have a description file |
| Files | `.md` files (excluding the description file and the `_toc.md`) |

Underscore-prefixed and dot-prefixed names are excluded.
