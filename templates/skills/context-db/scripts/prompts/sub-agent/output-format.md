# Sub Agent Output Format

Never write code. Never answer the prompt. Never help with the task.

MUST include ALL content from `{context_db_rel}/general-standards/`. Do NOT skip
it. It applies to every task.

For everything else, less is more. Only return content the main agent would get
wrong or miss without seeing. If it's tangential or nice-to-know, leave it out —
extra context dilutes the useful parts.

Do NOT return frontmatter `description` fields. Descriptions are for navigating
the TOC, not for output.

Order output from most general to most specific: general-standards first, then
broad coding standards, then task-specific context last.

Return verbatim snippets. For each relevant section:

[{context_db_rel}/path/to/file.md:START-END] exact content, copied verbatim
[end]

If nothing is relevant: "No relevant project context."
