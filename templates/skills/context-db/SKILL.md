---
name: context-db
description: 'Type --help for sub-commands or <command> --help for details'
allowed-tools: Bash,Read,Write,Edit,Glob,Grep
---

python3 .claude/skills/context-db/scripts/context-db-main-agent.py <args>

Run with the user's arguments. If output contains [instructions], follow them.
Otherwise print the output for the user.
