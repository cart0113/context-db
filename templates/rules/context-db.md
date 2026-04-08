This project uses `context-db/` — a hierarchical Markdown knowledge base
containing all project context, standards, conventions, and design decisions.

At the start of every conversation, before doing anything else:

1. Read `.claude/skills/context-db-manual/SKILL.md` to learn how context-db
   works.
2. Load the `context-db-manual` skill with `/context-db-manual`.
3. Run the TOC script shown in SKILL.md on `context-db/` to see all topics.
4. Read topics relevant to the user's request.

Do not write code, answer questions, or make suggestions until these steps are
complete. The context-db is the primary way you learn how this project works —
skipping it means you are working blind.
