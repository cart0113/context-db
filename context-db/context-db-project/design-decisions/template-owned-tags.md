---
description:
  Section tags like [read-mechanics] live in .md template files, not in the
  Python script — script just loads and prints
---

Tags (`[read-mechanics]`, `[context-usage]`, etc.) are in the `.md` files. The
script calls `print_template("read-mechanics", ...)` — load, fill, print.

`print_section()` exists only for dynamic content (e.g. wrapping user text in
`[update-user-instructions]`).

Three template directories in `prompts/`:

- `main-agent/` — core templates used by main-agent mode and reused by
  sub-agent. Read commands, write commands, command-specific instructions.
- `sub-agent/` — additional templates for the isolated `claude -p` sub-agent.
  Per-command role files (`role-prompt.md`, etc.) that combine identity, task
  description, and navigation constraints in one `[sub-agent-role]` block.
  Output format templates for each command type.
- `spawn/` — what the main agent sees to trigger the sub-agent. Per-command
  templates with the run command and usage instructions.

The sub-agent composes its system prompt from main-agent + sub-agent templates.
See `descriptive-tag-names.md` for tag naming convention.

Conditional templates: `update-commit.md` only prints when `--commit` flag is
set. `read-mechanics.md` prints for update only with `--commit` (so the agent
can look up commit standards from context-db).

No markdown headers in templates. No reminder blocks. User instructions always
last.
