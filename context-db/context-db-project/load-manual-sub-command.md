---
description:
  load-manual subcommand — loads a single instruction template by name. Used
  mid-conversation when the agent needs to refresh on a specific topic.
---

## What it does

`load-manual <section>` prints one prompt template. No compositing, no config.
Used when the agent needs instructions for a specific capability
mid-conversation (e.g., "how do I write to context-db?").

## Usage

    /context-db load-manual <section>

Run `--help` to see available sections with descriptions.

## Available sections

- `on-demand` — don't browse context-db, wait for /context-db commands
- `read-mechanics` — how to navigate context-db via TOC script
- `prompt` — instructions for prompt command
- `context-usage` — context-db is a map, not truth
- `write-mechanics` — how to edit context-db files
- `write-content-guide` — what belongs in context-db
- `persist-to-context-db` — use context-db, not auto-memory
- `pre-review` — check plan against standards before implementing
- `review` — review changes against conventions
- `update-general` — file learnings into context-db
- `update-commit` — how to write commit messages

## Design rationale

Startup instructions are now delivered via rule files
(`templates/rules/startup-*.md`) that users copy or symlink to
`.claude/rules/context-db.md`. Rules survive compaction and require no hook or
config. `load-manual` is the mid-conversation escape hatch for loading
individual instruction sections on demand.
