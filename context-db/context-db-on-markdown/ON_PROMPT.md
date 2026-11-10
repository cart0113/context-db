<!--
Everything in this file outside HTML comments is inlined on every
`/context-db prompt`, immediately before the user's instruction.
-->

When renaming or restructuring anything in this repo, update directly. No
backward-compat shims, no aliases, no fallback handlers for old names. If
callers break, update the callers.

`.claude/skills/context-db` is a symlink to `skill/context-db`. Edit the files
under `skill/`.

No unsolicited explanations. Don't explain code unless asked. Skip summary
recaps after edits.
