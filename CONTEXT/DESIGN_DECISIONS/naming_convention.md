---
title: Naming Convention
description: Why files are named after their parent folder rather than using fixed names
---

# Naming Convention

Files are named `<folder>.md` and `<folder>_toc.md` rather than fixed names like
`CONTEXT.yml` and `CONTEXT_TOC.md`.

## Rationale

- **Self-describing.** `CODING.md` tells you exactly what it describes. `CONTEXT.md`
  in a `CODING/` directory does not.
- **No collision.** If you have `CONTEXT/CODING/` and `CONTEXT/DATABASE/`, the files
  are `CODING.md` / `CODING_toc.md` and `DATABASE.md` / `DATABASE_toc.md`. All unique
  names, easy to search for.
- **Generalizes beyond CONTEXT/.** The convention works for any directory, not just
  ones named `CONTEXT`. A `docs/API/` directory could use `API.md` + `API_toc.md`.
- **Script simplicity.** The build script computes `foldername=$(basename "$dir")` and
  knows exactly which files to read and write. No special-casing.
