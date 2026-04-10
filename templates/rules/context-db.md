This project uses `context-db/` — a knowledge base with conventions, design
decisions, pitfalls, and project context.

BEFORE responding to the user, read context-db topics relevant to their request:

1. Run the TOC script to see what topics exist:
   `.claude/skills/context-db-manual/scripts/context-db-generate-toc.sh context-db/`
2. Read topics relevant to the task — conventions, standards, pitfalls for the
   area the user is asking about.
3. Then proceed with the task, informed by what you read.

Do NOT skip this for non-coding tasks. Writing docs, analysis, review, and
planning all benefit from project context.

Context-db is a hint, not truth. Always verify against the actual code.

For full instructions on reading and updating context-db: `/context-db-manual`
