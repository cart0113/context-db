---
description:
  SessionStart hook forces the agent to load context-db at conversation start —
  why CLAUDE.md alone was not enough and how the hook works
---

## Problem

Instructions in `~/.claude/CLAUDE.md` told the agent to load the context-db
skill at the start of every conversation. The agent read the instruction but
routinely ignored it. CLAUDE.md is context — guidance the model can choose not
to follow.

## Solution

A **SessionStart hook** injects a directive into the conversation before the
agent sees the user's first message. Combined with a `.claude/rules/` file, the
agent gets two reinforcing signals.

### Files

| File                                          | Role                                                   |
| --------------------------------------------- | ------------------------------------------------------ |
| `templates/hooks/session-start-context-db.sh` | Hook script — outputs mandatory load directive         |
| `templates/rules/context-db.md`               | Rule — tells agent to read SKILL.md and load the skill |
| `.claude/settings.local.json`                 | Wires the hook into `hooks.SessionStart`               |

### How it works

1. Claude Code fires SessionStart hooks on `startup` and `resume`.
2. The hook script prints text to stdout.
3. That text is injected into the conversation context before the first turn.
4. The rule file loads automatically and reinforces the same instruction.

### Why this is stronger than CLAUDE.md

- **CLAUDE.md** is loaded as user context — the model weighs it but can skip it.
- **SessionStart hooks** inject text at the very start of the session, before
  user input. The agent sees it as an immediate directive, not background
  guidance.
- **Rules** load automatically alongside CLAUDE.md but are presented as project
  rules, not general suggestions.

### If the rule is still not followed

1. Check the hook fires — run the script manually.
2. Check `settings.local.json` references the correct script path.
3. Escalate the rule language ("MANDATORY", "BLOCKING").
4. Add a project-level `CLAUDE.md` as a third reinforcement layer.

Hook + rule is the strongest enforcement available in Claude Code today.
