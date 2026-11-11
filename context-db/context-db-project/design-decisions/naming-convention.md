---
type: Decision
description:
  Why files are named after their parent folder rather than using fixed names
---

# Naming Convention

Each folder's descriptor is named `<folder>.md` rather than a fixed name like
`CONTEXT.md`. OKF has no rule for this (its issue #10 proposes the same idea),
so the descriptor is an ordinary concept with `type: Folder`.

## Rationale

- **Self-describing.** `CODING.md` tells you exactly what it describes.
  `CONTEXT.md` in a `CODING/` directory does not.
- **No collision.** If you have `context-db/coding/` and `context-db/database/`,
  the description files are `coding.md` and `database.md`. All unique names,
  easy to search for.
- **Generalizes beyond context-db/.** The convention works for any directory. A
  `docs/api/` directory uses `api.md`.
- **Script simplicity.** `toc` computes the folder basename and knows exactly
  which description file to look for. No special-casing.
