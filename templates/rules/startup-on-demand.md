This project uses a `context-db/` knowledge base — a hierarchical Markdown
repository of conventions, standards, design decisions, and pitfalls.

Do NOT browse or read `context-db/` on your own. The user will explicitly invoke
`/context-db` commands when they want you to incorporate project knowledge.

Available commands:

- `/context-db prompt "<request>"` — search for relevant context
- `/context-db pre-review` — check standards before coding
- `/context-db review` — review changes against conventions
- `/context-db update` — persist learnings to context-db
- `/context-db read-all <folder>` — exhaustively read a folder
- `/context-db load-manual <section>` — load detailed instructions for a
  capability
