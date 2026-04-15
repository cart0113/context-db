[sub-agent-output-format-review]

Write a review report. For each issue:

- Describe the problem clearly.
- Quote the relevant convention from context-db with its source path:

  Source: {context_db_rel}/path/to/file.md

  > exact quoted text from the convention file

Only flag issues supported by conventions in the knowledge base. Do not add
general code review opinions -- if it's not in context-db, don't flag it.

Never suggest fixes -- only identify problems.

If no convention issues are found, say so clearly.

[end sub-agent-output-format-review]
