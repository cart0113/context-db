#!/bin/bash
# SessionStart hook — directs the agent to read context-db before responding.
# Wire this up in .claude/settings.local.json under hooks.SessionStart.
#
# This hook and templates/rules/context-db.md must say the same thing.
# If you change one, change the other.

cat <<'EOF'
This project uses context-db/ — a knowledge base with conventions, design
decisions, pitfalls, and project context.

BEFORE responding to the user, read context-db topics relevant to their request:

1. Load the context-db-manual skill and make sure you have loaded its
   .claude/skills/context-db-manual/SKILL.md content.
2. This will inform you that you need to run the TOC script to see what topics
   exist:
   .claude/skills/context-db-manual/scripts/context-db-generate-toc.sh context-db/
3. Read topics relevant to the task — conventions, standards, pitfalls for the
   area the user is asking about.
4. Then proceed with the task, informed by what you read.
EOF
