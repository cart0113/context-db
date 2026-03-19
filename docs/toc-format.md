# TOC File Format

`<folder>_toc.md` files are fully generated. Never edit them.

## Example

```markdown
## Subfolders

- Shared coding standards *(read-only)*
  [coding/](coding/coding_toc.md)
- Schema and migration patterns
  [database/](database/database_toc.md)

## Files

- System components and data flow
  [architecture.md](architecture.md)
```

Each entry is a bullet with the description on the first line and the link on the second. Symlinked folders are marked *(read-only)*.

## Sections

Sections only appear when there are entries — an empty folder produces an empty TOC.

| Section | Contents |
|---------|----------|
| Subfolders | Subdirectories that have a description file |
| Files | `.md` files (excluding the description file and the `_toc.md`) |

Underscore-prefixed and dot-prefixed names are excluded.
