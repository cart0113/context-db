#!/bin/bash
[ "$CONTEXT_DB_SUBAGENT" = "1" ] && exit 0

python3 .claude/skills/context-db/scripts/context-db-main-agent.py load-manual || echo "CRITICAL: context-db load-manual failed. Tell the user immediately."
