<!--
Everything in this file outside HTML comments is added to every
`/context-db prompt`, immediately before the user's instruction. Edit it by hand
whenever you like.

Keep it to the few rules the agent must see every time: every line is read on
every run. An empty file adds nothing.
-->

When renaming or restructuring anything in this repo, update directly. No
backward-compat shims, no aliases, no fallback handlers for old names. If
callers break, update the callers.

`.claude/skills/context-db` is a symlink to `skill/context-db`. Edit the files
under `skill/`.

No unsolicited explanations. Don't explain code unless asked. Skip summary
recaps after edits.

Write to the knowledge base only when the user runs `/context-db update`. At
any other time, leave `context-db/` alone. If you learn something worth keeping, say
so in one line and suggest that command.
