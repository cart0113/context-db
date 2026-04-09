#!/bin/bash
# SessionStart hook — reminds the agent about context-db.
# Wire this up in .claude/settings.local.json under hooks.SessionStart.

cat <<'EOF'
This project has a context-db/ knowledge base with gotchas, checklists, and
design decisions. Run the TOC script to see topics:

.claude/skills/context-db-manual/scripts/context-db-generate-toc.sh context-db/

Read topics relevant to the task, then read the code.
EOF
