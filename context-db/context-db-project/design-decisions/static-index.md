---
type: Decision
description:
  Why index.md files are generated and committed inside each top-level folder
  while the list of top-level folders is printed on every call — reverses v0.0's
  fully dynamic TOC without reintroducing the per-user symlink problem. Also why
  the index is a flat Subfolders/Files list and not grouped by type.
---

# Static index inside a folder, dynamic listing above it

v0.0 had no committed table of contents. A script printed one for any folder on
demand. v0.1 commits a generated `index.md` in every folder of the project
folder and of each background folder.

## Why v0.0 went dynamic

A user can mount a private folder with a gitignored symlink. A committed listing
of `context-db/` would then either name a folder teammates do not have or omit
one the user does. No committed file can reflect per-user symlinks.

## Why that no longer forces everything to be dynamic

The problem exists only where symlinks are allowed, and v0.1 allows them only at
the top level of `context-db/`. So:

- The list of top-level folders is still generated on every `prompt`, by
  `folders_section()` in the script. Nothing committed depends on what a user
  has mounted. This is also why `context-db/` itself has no `index.md`.
- Inside a top-level folder every subfolder is real, so its `index.md` is the
  same for everyone and can be committed.

## What the static index buys

- The agent navigates with its file-read tool. No script call per level, no
  permission prompt, no interpreter needed on the read path.
- The knowledge base is browsable on GitHub, in Obsidian, and by any OKF
  consumer.
- It is the OKF-native form of progressive disclosure.

## The cost, and what contains it

Generated files in git can drift from the frontmatter they are derived from.
`index --check` fails the pre-commit hook and CI when they do, and `update` and
`wip` both end by regenerating. Merge conflicts in an `index.md` are resolved by
regenerating, never by hand.

## Flat, not grouped by type

OKF's reference implementation groups index entries under a heading per `type`.
context-db writes two fixed headings, `# Subfolders` and `# Files`. Folders hold
5–10 items, so type headings would add lines without helping the agent choose;
the description does the routing. Both layouts are valid OKF.

## A consequence for shared folders

The script refuses to write through a symlink, so a mounted folder's indexes are
generated in the repository that owns it. A background folder with no `index.md`
still works: `prompt` tells the agent to list the folder and read frontmatter.

Folders that hold no Markdown (images, scripts) are skipped entirely: no index,
no descriptor required.
