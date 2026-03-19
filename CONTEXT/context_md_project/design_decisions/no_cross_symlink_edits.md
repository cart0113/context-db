---
description: Why build_toc.sh never writes to directories that are symlinks
---

# No Cross-Symlink Edits

`build_toc.sh` skips any directory that is a symlink. It reads the `<folder>.md` from
a symlinked directory (to get the description for the parent's TOC table) but never
writes a `_toc.md` inside it.

## Rationale

- **Ownership.** A symlinked directory belongs to another project. Writing into it
  would modify files in a different repository — unexpected and potentially destructive.
- **Idempotency.** The external project runs its own `build_toc.sh` to manage its own
  TOC files. Having two projects write to the same files creates race conditions and
  merge conflicts.
- **Simplicity.** The alternative (detecting symlinks, resolving paths, checking
  ownership) adds complexity for a marginal benefit. If you need the symlinked
  directory's TOC rebuilt, run the script from that project.

Symlinked directories are automatically marked *(read-only)* in the parent's generated
TOC to signal to the LLM that the resource is externally managed.
