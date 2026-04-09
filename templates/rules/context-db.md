This project uses `context-db/` — a hierarchical Markdown knowledge base that
documents how this project works: architecture, design decisions, gotchas,
checklists, and conventions.

**Context-db is a hint, not truth.** It can be stale, incomplete, or wrong. The
code is always the source of truth. Never skip reading code because context-db
"already explained" what you need.

## Workflow — follow this order

1. Run the TOC script to see what's available:
   ```
   .claude/skills/context-db-manual/scripts/context-db-generate-toc.sh context-db/
   ```
2. **Read relevant context-db topics** before exploring code with Glob, Grep, or
   Agent. This prevents wasting time on blind exploration.
3. **Then read the actual code.** Always verify what context-db says against the
   real code before making changes.

Both steps are required. Context-db without code leads to stale assumptions.
Code without context-db leads to blind exploration and missed gotchas.

**Do NOT delegate context-db reading to a subagent.** Read topics yourself in
the main conversation so the knowledge informs all subsequent decisions.

## Verify before acting

Before acting on context-db claims:

- If it names a file path, check the file exists.
- If it names a function, flag, or config key, grep for it.
- If it describes architecture or data flow, read the actual modules.
- If context-db conflicts with the code, **trust the code** and flag the
  discrepancy to the user.
