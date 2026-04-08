#!/bin/bash
# SessionStart hook — injected into conversation context before the first turn.
# Wire this up in .claude/settings.local.json under hooks.SessionStart.

SKILL_FILE="$CLAUDE_PROJECT_DIR/.claude/skills/context-db-manual/SKILL.md"

cat <<'EOF'
MANDATORY FIRST ACTION — do this before responding to the user:

1. Read the context-db SKILL.md file to learn how context-db works.
2. Load the context-db-manual skill by invoking: /context-db-manual
3. Run the TOC script on context-db/ to see all available topics.
4. Read topics relevant to the user's request.

Do NOT skip these steps. Do NOT respond to the user until you have completed them.
EOF

# Also emit the SKILL.md path so Claude knows exactly where to read
if [ -f "$SKILL_FILE" ]; then
  echo ""
  echo "SKILL.md location: $SKILL_FILE"
fi
