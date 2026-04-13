---
name: context-db
description:
  'Project knowledge base {read-manual, prompt, pre-review, review, update,
  maintain}'
allowed-tools: Bash,Read,Write,Edit,Glob,Grep
---

Run the dispatcher with the user's sub-command and arguments:

```
python3 .claude/skills/context-db/scripts/context-db-main-agent.py <command> [args]
```

Commands: {read-manual, prompt, pre-review, review, update, maintain}
