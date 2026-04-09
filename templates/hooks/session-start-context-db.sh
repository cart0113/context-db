#!/bin/bash
# SessionStart hook — tells the agent to load the context-db skill.
# Wire this up in .claude/settings.local.json under hooks.SessionStart.

cat <<'EOF'
Read .claude/skills/context-db-manual/SKILL.md, then run the TOC script on context-db/.
EOF
