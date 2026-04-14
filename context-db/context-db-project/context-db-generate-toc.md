---
description:
  How the TOC script works — frontmatter parsing, description file lookup,
  symlink resolution, and known edge cases
---

# context-db-generate-toc.py

The Python TOC script generates table-of-contents on the fly by reading YAML
frontmatter from `.md` files and printing description/path pairs to stdout.

## Behavior an agent would get wrong

**Files without frontmatter are invisible.** The script only lists `.md` files
with a `description` field in YAML frontmatter. No frontmatter = no TOC entry,
no error. A newly created file won't appear until frontmatter is added.

**Multi-line descriptions in frontmatter-only files.** When a multi-line
description appears in a folder descriptor (frontmatter only, no body), the
parser must handle the closing `---` as the last line. This edge case is covered
by tests but easy to break if the parser is modified. Prettier with
`proseWrap: always` triggers this on descriptions longer than ~60 characters.

**Symlinks use the real folder name for description lookup.** When
`general-coding-standards/` symlinks to
`external/repo/context-db/coding-standards/`, the script looks for
`coding-standards.md` (real name), not `general-coding-standards.md`. Symlinks
can be named freely without renaming description files in the source repo.

## Description file lookup order

1. `<foldername>.md`
2. `<foldername>-instructions.md`
3. `SKILL.md`, `CONTEXT.md`, `AGENT.md`, `AGENTS.md`

## Skipping rules

Names starting with `_` or `.` are always skipped (`_drafts/`, `.hidden/`).
