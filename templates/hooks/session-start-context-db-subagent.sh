#!/bin/bash
# SessionStart hook for context-db subagent mode.
# Wire this up in .claude/settings.local.json under hooks.SessionStart.
#
# Calls context-db-sub-agent.py instructions to generate config-aware instructions.
# This hook and templates/rules/context-db-subagent.md reinforce each other.

# Skip if we're inside a subagent call (prevents noise in recursive calls)
[ "$CONTEXT_DB_SUBAGENT" = "1" ] && exit 0

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
AGENT_SCRIPT=""

# Find context-db-sub-agent.py — try symlink path first, then resolved
for candidate in \
    "$SCRIPT_DIR/../skills/context-db-subagent/scripts/context-db-sub-agent.py" \
    "$(cd "$SCRIPT_DIR" && pwd -P)/../skills/context-db-subagent/scripts/context-db-sub-agent.py" \
    ".claude/skills/context-db-subagent/scripts/context-db-sub-agent.py"; do
    if [ -f "$candidate" ]; then
        AGENT_SCRIPT="$candidate"
        break
    fi
done

if [ -n "$AGENT_SCRIPT" ] && command -v python3 >/dev/null 2>&1; then
    python3 "$AGENT_SCRIPT" instructions
else
    # Fallback: static instructions if python3 or script unavailable
    cat <<'EOF'
This project has a knowledge expert. You MUST follow these instructions.

  python3 .claude/skills/context-db-subagent/scripts/context-db-sub-agent.py <mode> "<message>"

  user-prompt: Run on every user prompt. Pass the user's exact prompt. Do not skip it, do not ask.
  code-review: Run after code changes. Pass a summary of changes made. Ask the user before running.
  update-context-db: Run after completing work. Pass what you learned — corrections, conventions, pitfalls. Do not skip it, do not ask.
EOF
fi
