---
description:
  Why show_toc.sh resolves symlinks for description lookup but treats them as
  read-only boundaries
---

# Symlink Handling

`show_toc.sh` follows symlinked directories to read their content and include
them in the parent's TOC output, but treats them as boundaries owned by another
project.

## Behavior

- Symlinked subdirectories appear as entries in the parent TOC (description is
  read using the **real** folder name, not the symlink name)
- The agent can run `show_toc.sh` on symlinked directories to see their contents
- The script never writes anything — it only prints to stdout

## Real Folder Name Resolution

When a symlink points to a directory with a different name (e.g.,
`general-coding-standards/` -> `external/repo/context-db/coding-standards/`),
the script resolves the symlink and looks for the description file using the
**real** folder name (`coding-standards.md`), not the symlink name. This allows
symlinks to be named freely without requiring description file renames in the
source repo.

## Use Case: Private Context via Symlink + .gitignore

This pattern enables pulling context from external repos into your project tree
without committing the content:

1. Clone or symlink external repos into your project
2. Symlink specific context-db folders into your `context-db/` directory
3. Add the symlinks to `.gitignore`
4. Your agent sees them in the TOC; other users' agents don't

Because `show_toc.sh` generates TOCs on the fly, there are no static files that
would get out of sync — the symlinked folders simply appear for whoever has
them.

See `cross-project-sharing.md` for the full pattern with git-sync, submodules,
and local symlinks.
