---
description:
  Why build_toc.sh never writes into symlinked directories but does follow them
  for TOC entries
---

# No Cross-Symlink Edits

`build_toc.sh` follows symlinked directories to read their content and include
them in the parent's TOC, but never writes TOC files into them.

## Behavior

- Symlinked subdirectories appear as entries in the parent TOC (description is
  read using the **real** folder name, not the symlink name)
- The script never writes `-toc.md` files inside a symlinked directory
- Recursion stops at the symlink boundary

## Rationale

- **Ownership.** A symlinked directory belongs to another project. Writing into
  it would modify files in a different repository.
- **Idempotency.** The external project runs its own `build_toc.sh`. Two
  projects writing to the same files creates conflicts.
- **Read-only repos.** When symlinks point into sparse checkouts managed by
  git-sync with `read-only: true`, any writes would dirty those repos and block
  sync.

## Real Folder Name Resolution

When a symlink points to a directory with a different name (e.g.,
`general-coding-standards/` → `external/repo/context-db/coding-standards/`),
`find_desc_file` resolves the symlink and looks for the description file using
the **real** folder name (`coding-standards.md`), not the symlink name. This
allows symlinks to be named freely without requiring description file renames in
the source repo.

## Use Case: Private Context via git-sync

This pattern enables pulling context from external repos into your project tree
without committing the content:

1. git-sync clones repos into `external/` with sparse checkout
2. Symlinks in `context-db/` point to specific subdirectories
3. `build_toc.sh` includes the symlinked content in parent TOCs
4. The external repos, symlinks, and private config are all gitignored

See git-sync's `.git-sync-private.yaml` documentation for the full pattern.
