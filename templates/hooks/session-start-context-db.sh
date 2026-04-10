#!/bin/bash
# SessionStart hook — points the agent to context-db.
# Wire this up in .claude/settings.local.json under hooks.SessionStart.
#
# This hook and templates/rules/context-db.md must say the same thing.
# If you change one, change the other.

cat <<'EOF'
This project uses context-db/ — a hierarchical Markdown knowledge base that
documents gotchas, design decisions, and cross-file connections — things you
can't derive from reading the code alone. It does not contain everything — it's
a starting point, a map, a hint — but helps you avoid known problems and orient
yourself in a project quickly.

Before starting any coding task, load the context-db skill:

  /context-db-manual

If the skill is unavailable, read the manual directly:

  Read .claude/skills/context-db-manual/SKILL.md

Follow its instructions for reading and updating the knowledge base.
EOF
