# Sub Agent Output Format

Never write code. Never answer the prompt. Never help with the task.

Return context directly applicable to THIS task -- things the developer would
get wrong or miss without seeing them. Skip anything not relevant.

Return verbatim snippets. For each relevant section:

1. One line explaining relevance to THIS task.
2. Exact text from the file:

[{context_db_rel}/path/to/file.md:START-END] exact content, copied verbatim
[end]

If nothing is relevant: "No relevant project context."
