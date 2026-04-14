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

- `read-mechanics.md` — TOC navigation (all commands)
- `context-usage.md` — "starting point, verify against project" (read commands)
- `write-file-format.md` — frontmatter, structure (write commands)
- `write-content-guide.md` — what belongs, brevity (write commands)
- `main-agent-{command}.md` — command-specific, includes don't-self-invoke

No markdown headers in templates. No reminder blocks. User instructions always
last.

Sub-agent templates (`system-*.md`, `user-*.md`) still use the old pattern —
rework pending after main-agent testing.
