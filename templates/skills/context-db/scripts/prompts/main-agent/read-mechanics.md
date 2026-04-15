# Read Mechanics

`{context_db_rel}/` is this project's knowledge base. Browse what's available
with the TOC script:

python3 {toc} {context_db_rel}/

The TOC script lists descriptions for every file and subfolder at that level.
Use descriptions to judge relevance before reading or drilling in:

- If a file's description indicates it's directly relevant to your task, read it
  (by design, files are around ~100 lines).
- If a subfolder's description suggests it contains directly relevant content,
  run the TOC script on it and repeat.
- Skip files and subfolders whose descriptions don't suggest direct relevance.
  Be selective — reading everything wastes time and dilutes useful context.

If `{context_db_rel}/general-standards/` exists, you MUST read every file in it.
These are global standards that apply to ALL tasks — like a CLAUDE.md. Do NOT
skip them. Do NOT filter them by relevance. Read them first, before anything
else.
