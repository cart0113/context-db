# Sub Agent Output Format

Never write code. Never answer the prompt. Never help with the task.

MUST include ALL content from `{context_db_rel}/general-standards/`. Do NOT skip
it. It applies to every task.

For everything else, only return context clearly relevant to the Main Prompt —
things someone would get wrong or miss without seeing them.

Do NOT return frontmatter `description` fields. Descriptions are for navigating
the TOC, not for output.

Order output from most general to most specific: general-standards first, then
broad coding standards, then task-specific context last.

Return verbatim snippets. For each relevant section:

[{context_db_rel}/path/to/file.md:START-END] exact content, copied verbatim
[end]

If nothing is relevant: "No relevant project context."
