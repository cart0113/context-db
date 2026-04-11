---
description:
  How to install subagent mode — .claude-project symlink, .contextdb.json
  config, switching between manual and subagent modes
---

# Installing Subagent Mode

## Prerequisites

- Python 3 (stdlib only, no pip packages)
- Claude CLI (`claude` command available)
- context-db-manual skill installed (subagent uses its TOC script)

## Two .claude-project variants

GIT_STANDARDS ships two `.claude-project` folders:

- `.claude-project` — manual mode (agent reads context-db directly)
- `.claude-project-context-db-subagent` — subagent mode (isolated model
  navigates context-db)

Switch by changing which one your project's `.claude` symlink points to:

```bash
# Switch to subagent mode
rm .claude
ln -s ../GIT_STANDARDS/templates/.claude-project-context-db-subagent .claude

# Switch back to manual mode
rm .claude
ln -s ../GIT_STANDARDS/templates/.claude-project .claude
```

## Config file

Copy `templates/contextdb.json` to `.contextdb.json` in the project root. This
file should be in `.gitignore` — different developers may want different models
or behaviors.

```json
{
  "modes": {
    "ask": { "model": "haiku", "behavior": "automatic", "frequency": "always" },
    "review": { "model": "sonnet", "behavior": "confirm" },
    "maintain": { "model": "sonnet", "behavior": "automatic" }
  }
}
```

### Config options

**model:** `haiku` (cheap/fast), `sonnet` (balanced), `opus` (best judgment).
One model per mode — the configured model handles the entire call.

**behavior:** `automatic` (call without asking), `confirm` (ask user first),
`skip` (disable this mode).

**frequency** (ask mode only): `always` (every prompt), `new` (topic changes),
`major` (significant new work only).
