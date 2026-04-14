---
description:
  Why the TOC script resolves symlinks for description lookup but treats them as
  read-only boundaries
---

# Symlink Handling

The TOC script follows symlinked directories to read their content and include
them in the parent's TOC output, but treats them as boundaries owned by another
project.

## Real Folder Name Resolution

When a symlink points to a directory with a different name (e.g.,
`general-coding-standards/` -> `external/repo/context-db/coding-standards/`),
the script resolves the symlink and looks for the description file using the
**real** folder name (`coding-standards.md`), not the symlink name. Symlinks can
be named freely without requiring description file renames in the source repo.

## Private Context via Symlink + .gitignore

Symlink external context-db folders into your `context-db/` directory and
`.gitignore` them. Your agent sees them in the TOC; teammates' agents don't.
Because TOCs are generated on the fly, there are no static files to get out of
sync.

See `cross-project-sharing.md` for the full pattern.
