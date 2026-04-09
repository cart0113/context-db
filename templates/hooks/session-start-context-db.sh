#!/bin/bash
# SessionStart hook — points the agent to context-db.
# Wire this up in .claude/settings.local.json under hooks.SessionStart.

echo "This project uses context-db. Read .claude/skills/context-db-manual/SKILL.md then run:"
echo ""
echo "  .claude/skills/context-db-manual/scripts/context-db-generate-toc.sh context-db/"
