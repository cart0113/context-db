---
description:
  Folder size rules, description maintenance, and post-session update checklist
---

## Folder rule — 5 to 10 items per folder

The system depends on agents navigating the tree without reading everything.
Each level must be small enough to scan at a glance.

- **5–10 items per folder.** No exceptions.
- When a folder exceeds this, split into subfolders with meaningful hierarchy.
- On any update, reconsider whether the file still belongs and whether the
  folder has grown too large.

The folder tree is a decision tree: each node should halve the search space.

## Keep descriptions current

After ANY change — new file, edit, rename, delete — ensure every affected file's
`description` accurately reflects its content. Stale descriptions actively
mislead future agents. This is the most important maintenance rule.

## Update checklist

After every session where you touched the codebase or learned something new:

1. **Capture** — Create or update documents with new knowledge.
2. **Summarize** — Rewrite every affected `description` to be accurate.
3. **Reorganize** — Check folder sizes; split or merge to stay at 5–10 items.
4. **Verify** — Run `show_toc.sh` on affected folders. Does the TOC make sense
   to a cold reader in two hops? If not, fix it.
