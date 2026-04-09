This project uses `context-db/` — a hierarchical Markdown knowledge base that
documents how this project works: architecture, design decisions, gotchas,
checklists, and conventions. Use it to understand the project before you read
the code.

## MANDATORY workflow — follow this order

1. Run the TOC script to see what's available:
   ```
   .claude/skills/context-db-manual/scripts/context-db-generate-toc.sh context-db/
   ```
2. **Read the context-db topics relevant to the user's request.** This is not
   optional — do it BEFORE exploring code with Glob, Grep, or Agent. The
   context-db tells you how the project is structured, where things live, and
   what pitfalls to avoid. This prevents wasting time on blind exploration.
3. **Then read the actual code.** Context-db orients you; the code is the source
   of truth. Always verify what context-db says against the real code before
   making changes.

Both steps are required. Context-db without code leads to stale assumptions.
Code without context-db leads to blind exploration and missed gotchas.

Skip topics that are clearly irrelevant. But when in doubt, read the topic — it
is faster than grepping the entire codebase.

**Do NOT delegate context-db reading to a subagent.** Read topics yourself in
the main conversation so the knowledge informs all subsequent decisions.
