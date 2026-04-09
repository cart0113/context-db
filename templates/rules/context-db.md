This project uses `context-db/` — a hierarchical Markdown knowledge base
containing gotchas, checklists, and design decisions.

At the start of every conversation, run the TOC script to see what's available:

```
.claude/skills/context-db-manual/scripts/context-db-generate-toc.sh context-db/
```

Read only topics relevant to the user's request. Skip what you don't need. Then
read the actual code — context-db orients you, the code is the truth.
