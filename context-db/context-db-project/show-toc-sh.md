---
description:
  How show_toc.sh works — awk-based frontmatter parsing, multi-line description
  handling, and known edge cases
---

# show_toc.sh

`bin/show_toc.sh` is the core script. It generates TOCs on the fly by reading
YAML frontmatter from `.md` files and printing description/path pairs to stdout.

## Frontmatter parsing

The `read_field` function uses awk to extract a named field from YAML
frontmatter (the block between `---` delimiters). It handles:

- **Single-line values**: `description: Some text` — matched and printed
  immediately.
- **Multi-line values** (YAML block scalar style): `description:` on its own
  line, followed by indented continuation lines. The awk joins them with spaces.
- **Fenced YAML fallback**: If standard frontmatter yields nothing, a second awk
  pass checks for ` ```yaml description ` fenced blocks (legacy format).

## Multi-line frontmatter edge case (fixed 2026-04-06)

**Problem**: When a multi-line description appeared in a frontmatter-only file
(like a folder description file ending with `---` as the last line), the
description was silently lost. The TOC showed `(no description)`.

**Root cause**: The awk parser uses a front-matter counter (`fc`). The closing
`---` increments `fc` to 2 and calls `next`, jumping to the next input line. But
in a frontmatter-only file, there IS no next line — so the `fc >= 2` block that
would print the accumulated value never fires.

**Fix**: Added `END` blocks to both awk passes. The `END` block fires after all
input is consumed (including after `exit`). A `done` flag prevents double
printing — set to 1 before every `exit`, checked in `END`.

**Why this matters**: prettier with `proseWrap: always` wraps long descriptions
to multiple lines. Folder description files are frontmatter-only. These two
facts together trigger this edge case on any description longer than ~60
characters.

## Description file lookup

`find_desc_file` searches for the folder's description file in this order:

1. `<foldername>.md`
2. `<foldername>-instructions.md`
3. `SKILL.md`, `CONTEXT.md`, `AGENT.md`, `AGENTS.md`

For symlinked folders, the script resolves the real folder name (via `pwd -P`)
for description file lookup.

## Skipping rules

Names starting with `_` or `.` are always skipped. This is how `_drafts/` and
`.hidden/` folders stay out of the TOC.
