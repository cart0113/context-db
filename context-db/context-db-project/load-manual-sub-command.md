---
description:
  load-manual subcommand — concatenates instruction templates into agent
  context. Configured by .context-db.json, overridden by CLI flags.
---

## What it does

`load-manual` stitches together prompt template files and prints them as a
single block. The session-start hook calls it with no flags (uses config
defaults). Users can call it manually after compaction or whenever the agent
needs instructions reloaded.

Always prints: `This project uses a context-db/ knowledge database.`

## CLI flags

Each template is a named flag. With no flags, uses the `load-manual` list from
`.context-db.json`. With flags, loads only those sections in canonical order:

1. `--read-mechanics` — how to navigate context-db via TOC script
2. `--prompt` — instructions for prompt command
3. `--context-usage` — context-db is a map, not truth
4. `--write-mechanics` — how to edit context-db files
5. `--write-content-guide` — what belongs in context-db
6. `--pre-review` — check plan against standards
7. `--review` — review changes against conventions
8. `--update-general` — file learnings into context-db
9. `--update-commit` — how to write commit messages

`--on-demand` is special: tells the agent not to browse context-db on its own,
wait for explicit `/context-db` commands. Cannot be combined with other flags.
This is the default configuration.

## Config file

`.context-db.json` in the project root. Supports `//` comments (JSONC). The
`load-manual` key is a list of `directory/name` template refs:

```json
{
  "load-manual": ["main-agent/on-demand"]
}
```

## Example configurations

### On-demand only (default) — agent knows context-db exists but won't touch it

```json
{
  "load-manual": ["main-agent/on-demand"]
}
```

### Read + respond to prompts (main agent handles everything)

```json
{
  "load-manual": [
    "main-agent/read-mechanics",
    "main-agent/context-usage",
    "main-agent/prompt"
  ]
}
```

### Full read + write instructions loaded at session start

```json
{
  "load-manual": [
    "main-agent/read-mechanics",
    "main-agent/prompt",
    "main-agent/context-usage",
    "main-agent/write-mechanics",
    "main-agent/write-content-guide",
    "main-agent/update-general"
  ]
}
```

## Design rationale

- **Why flags instead of positional args?** `--help` becomes self-documenting —
  shows every available section and the order they emit in.
- **Why canonical order?** Sections build on each other (read before write,
  etc). Flags can be given in any order; output is always correct.
- **Why --on-demand?** Most sessions don't need context-db loaded. The agent
  should know it exists but stay out until asked.
