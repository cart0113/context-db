---
type: Decision
description:
  Why there are no index.md files — context-db builds each folder's OKF index on
  demand with the hidden `toc` helper, the way v0.0's TOC script did, and the
  agent is told how on every command that reads the knowledge base. Reverses
  v0.1's committed, generated indexes (owner decision, 2026-11-11). Also why the
  listing is flat Subfolders/Files and not grouped by type.
---

# Dynamic indexing

`toc <folder>` reads the frontmatter of a folder's files and subfolders and
prints the listing in OKF's `index.md` layout. Nothing is written. The agent
runs it every time it looks into a folder, and again on a subfolder whose
description matches. `toc --check` is the format check, run after writes, by
the pre-commit hook, and in CI.

OKF lets a folder carry an `index.md` and only constrains its layout if one
exists, so building it on demand is conformant. The docs present it as a
feature: this is how context-db implements OKF's index.

## History

- v0.0 printed a TOC on demand with a script, after committed `-toc.md` files
  broke on per-user symlinked folders.
- v0.1 briefly committed a generated `index.md` per folder, for file-read
  navigation and GitHub browsing. That needed a regenerate step after every
  write, a CI drift check, a rule for merge conflicts, a gitignore filter so
  private notes stayed out, and owning repositories generating indexes for
  shared folders.
- On 2026-11-11 the owner reversed it: "I liked the way I was doing it before",
  "Before this v0.1 work, that was a major part of the system." The v0.0 way
  "was working well".

## The navigation instruction is core text

The owner: "this is just something fundamental in the core instructions given
to the agent on every skill invocation." It lives in one file,
`skill/context-db/prompts/navigate.md` (v0.0 called it Read Mechanics), and
`prompt`, `update`, `maintain`, `wip`, and `wip --cleanup` all include it.
`SKILL.md` repeats it. `prompt` builds no listing itself; it only tells the
agent how to call the script. A test fails if a reading command leaves it out.

## Costs accepted

- Each folder costs the agent one script call instead of a file read.
- GitHub and Obsidian show folders without the descriptions.

## Flat, not grouped by type

OKF's reference implementation groups index entries under a heading per `type`.
context-db prints two fixed headings, `# Subfolders` and `# Files`. Folders hold
5–10 items, so type headings would add lines without helping the agent choose;
the description does the routing.
