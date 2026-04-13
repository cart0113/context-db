---
description:
  How to install subagent mode — symlink switching, .contextdb.json should be
  gitignored, full review-type defaults to opus
status: deprecated
---

# Installing Subagent Mode

## Switching modes

GIT_STANDARDS ships two `.claude-project` folders. Switch by changing which one
your project's `.claude` symlink points to:

```bash
# Subagent mode
ln -sfn ../GIT_STANDARDS/templates/.claude-project-context-db-subagent .claude

# Manual mode
ln -sfn ../GIT_STANDARDS/templates/.claude-project .claude
```

## Config

Copy `templates/contextdb.json` to `.contextdb.json` in the project root. This
file should be in `.gitignore` — different developers may want different models
or frequency settings.

Only user-prompt is enabled by default. Enable other modes by adding them to
`.contextdb.json`. The script's `DEFAULT_CONFIG` shows all available options.

Non-obvious config behavior:

- `full` review-type automatically upgrades to opus if no model is explicitly
  set (context-db review doesn't need opus-level judgment, but general review
  benefits from it)
- The main agent never reads `.contextdb.json` — instructions mode translates it
  into directives
