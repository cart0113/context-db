---
description:
  load-manual subcommand — concatenates instruction templates into agent
  context. Replaces init. Configured by .context-db.json, overridden by CLI
  args.
---

## What it does

`load-manual` stitches together any combination of prompt template files and
prints them as a single block. Templates can come from any directory —
`main-agent/`, `sub-agent/`, `spawn/`. The session-start hook calls it with no
args (uses config defaults). Users can call it manually after compaction or
whenever the agent needs instructions reloaded.

Replaces the old `init` subcommand. `init` was limited to main-agent templates
and had a separate config key. `load-manual` is the universal version.

## How it works

Template refs use `directory/name` format — e.g. `main-agent/read-mechanics`,
`sub-agent/role-review`. The directory maps to `prompts/<directory>/` and the
name maps to `<name>.md`.

Resolution order:

1. CLI args given — use those, ignore config entirely
2. No CLI args — use the `load-manual` list from `.context-db.json`
3. No config file — use hardcoded defaults (read-mechanics +
   persist-to-context-db)

## Config file

`.context-db.json` in the project root. Gitignored (per-machine config).

## Example configurations

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

### Read + prompt via main agent, review/pre-review via sub-agent spawn

```json
{
  "load-manual": [
    "main-agent/read-mechanics",
    "main-agent/context-usage",
    "main-agent/prompt",
    "spawn/pre-review",
    "spawn/review"
  ]
}
```

### Prompt, pre-review, review all via sub-agent

```json
{
  "load-manual": [
    "main-agent/read-mechanics",
    "spawn/prompt",
    "spawn/pre-review",
    "spawn/review"
  ]
}
```

## CLI override

Pass template refs directly to skip config:

```
python3 .../context-db-main-agent.py load-manual main-agent/read-mechanics main-agent/write-mechanics
```

Useful for one-off reloads — e.g. after compaction, load just the write
instructions you need for the current task.

## Design rationale

- **Why replace init?** init was a separate code path that did the same thing
  (concatenate templates) but only supported main-agent templates and used a
  different config key. One command, one config key, any template directory.
- **Why CLI override?** Users reload instructions mid-session. Editing config
  just to reload different templates is friction. Positional args are simpler.
- **Why no --all flag?** The config IS the "all" — it defines the default set.
  An --all flag would need its own hardcoded list, duplicating the config.
