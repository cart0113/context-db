---
type: Decision
description:
  Why frontmatter is limited to type, description, optional status, and branch
  on wip files — and why OKF's tags, trust, provenance, and timestamp keys are
  tolerated but never written
---

# Frontmatter fields

| Key           | Rule                                                            |
| ------------- | --------------------------------------------------------------- |
| `type`        | Required by OKF. A short free-form label.                       |
| `description` | Required by context-db. The routing decision shown in the index. |
| `status`      | Optional: `draft`, `stable` (the default), `deprecated`.        |
| `branch`      | Optional, on `wip/` files only.                                 |

## The principle

A key earns its place only if it (1) cannot be derived from the filesystem or
git, (2) changes what an agent does, and (3) costs almost nothing to maintain.

- `type` barely passes on its own merits. It is here because it is the one key
  OKF conformance requires. The vocabulary is suggested, not enforced, so it
  never blocks a write.
- `status` changes behavior at no cost: the index shows `[draft]` or
  `[deprecated]` and nothing when stable. v0.0's extra values (`experiment`,
  `work-in-progress`, `refactor`) are gone; that content now lives in `wip/`.
- `branch` lets `/context-db wip` tell another branch's plan from a finished
  one.

## Keys OKF offers that are deliberately not written

- **`generated`, `verified`, `stale_after`, `sources`.** Git blame and git log
  already record who changed what and when for an in-repo bundle. A trust field
  nobody maintains creates false confidence, which is worse than no field.
- **`tags`.** Needs a controlled vocabulary. The description and the folder
  hierarchy already do discovery.
- **`title`.** Redundant with the H1. The index takes its link text from
  `title` if present, else the first H1, else the filename.

Lint ignores unknown keys, so a bundle that carries them still passes.
