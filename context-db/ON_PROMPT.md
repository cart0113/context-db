---
description:
  Inlined automatically on every /context-db prompt for this repo. Working-style
  rules every agent must follow when changing context-db.
---

# On Prompt

When renaming or restructuring anything in this repo, update directly. No
backward-compat shims, no aliases, no fallback handlers for old names. If
callers break, update the callers.

The skill scripts under `.claude/skills/context-db/` are a symlink to
`templates/skills/context-db/` — edit the files under `templates/`, never the
`.claude/` copies.

No unsolicited explanations. Don't explain code unless asked. Skip summary
recaps after edits.
