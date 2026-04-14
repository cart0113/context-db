---
description:
  Section tags like [read-mechanics] live in .md template files, not in the
  Python script — script just loads and prints
---

Tags (`[read-mechanics]`, `[context-usage]`, etc.) are in the `.md` files. The
script calls `print_template("read-mechanics", ...)` — load, fill, print.

`print_section()` exists only for dynamic content (e.g. wrapping user text in
`[update-user-instructions]`).

Main-agent output composes these templates:

- `read-mechanics.md` — TOC navigation (read commands; also update with
  --commit)
- `context-usage.md` — "starting point, verify against project" (read commands)
- `write-mechanics.md` — frontmatter, structure, TOC flags (write commands)
- `write-content-guide.md` — what belongs, brevity (write commands)
- `persist-to-context-db.md` — memory-system directive (update)
- `update-general.md` — session-first thinking, brevity (update)
- `update-commit.md` — commit instructions (update with --commit only)
- `prompt.md`, `pre-review.md`, `review.md` — command-specific instructions
- `maintain-instructions.md` — audit workflow (maintain)

Conditional templates: `update-commit.md` only prints when `--commit` flag is
set. `read-mechanics.md` prints for update only with `--commit` (so the agent
can look up commit standards from context-db).

No markdown headers in templates. No reminder blocks. User instructions always
last.
