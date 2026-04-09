#!/bin/bash
# SessionStart hook — points the agent to context-db.
# Wire this up in .claude/settings.local.json under hooks.SessionStart.

echo "MANDATORY: This project uses context-db/ to document how the project works."
echo "You MUST read relevant context-db topics to understand the project BEFORE"
echo "exploring code with Glob, Grep, or Agent. Then read the actual code to verify."
echo "Do NOT skip context-db. Do NOT delegate context-db reading to a subagent."
echo ""
echo "Run this first:"
echo "  .claude/skills/context-db-manual/scripts/context-db-generate-toc.sh context-db/"
echo ""
echo "Then Read the topics that match the user's request, then read the code."
