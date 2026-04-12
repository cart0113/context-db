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
or settings.

```json
{
  "user-prompt": { "model": "haiku", "when": "major" },
  "code-review": {
    "model": "sonnet",
    "when": "major",
    "review-type": "context-db"
  },
  "update-context-db": { "model": "sonnet", "when": "major" }
}
```

### Config options

**model:** `haiku` (cheap/fast), `sonnet` (balanced), `opus` (best judgment).
One model per mode — the configured model handles the entire call. Exception:
`full` review-type defaults to opus if no model is explicitly set.

**when:** `always` (every prompt/change), `major` (significant new work only),
`never` (disabled).

**review-type** (code-review only): `context-db` (only flag convention issues)
or `full` (convention issues + general code review).

The main agent never reads this file. The `instructions` mode reads it and
returns the right instructions.
