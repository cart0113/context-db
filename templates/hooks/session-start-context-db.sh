#!/bin/bash
# Session-start hook for context-db.
# Calls context-db-main-agent.py init to generate startup instructions.
# Skips if inside a sub-agent call (prevents recursion).

[ "$CONTEXT_DB_SUBAGENT" = "1" ] && exit 0

SCRIPT=""
for candidate in \
    "$(cd "$(dirname "$0")/.." && pwd)/skills/context-db/scripts/context-db-main-agent.py" \
    ".claude/skills/context-db/scripts/context-db-main-agent.py"; do
    if [ -f "$candidate" ]; then
        SCRIPT="$candidate"
        break
    fi
done

if [ -n "$SCRIPT" ] && command -v python3 >/dev/null 2>&1; then
    python3 "$SCRIPT" init
else
    echo "context-db: This project has a context-db knowledge base."
    echo "Use /context-db to access it."
fi
