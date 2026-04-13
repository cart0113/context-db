Update the project's context-db knowledge base with learnings from this session.

## How to navigate context-db

`{context_db_rel}/` is a B-tree of markdown files. Browse with the TOC script:

python3 {toc} {context_db_rel}/

Drill into folders to understand what's already documented.

To drill into a subfolder: python3 {toc} {context_db_rel}/<subfolder>/ To read a
file: Read {context_db_rel}/<subfolder>/file.md

## Steps

1. Run: git diff — understand what changed this session
2. Navigate context-db — understand what's already documented
3. Update existing files or create new ones for genuinely new topics

## What belongs

Only file what the code can't tell you. Conventions, corrections, pitfalls,
design rationale invisible in the code.

Do NOT add: code summaries, what exists, how it's structured, step-by-step
instructions, anything derivable in 30 seconds with ls/grep/read.

## File format

- Every .md file needs YAML frontmatter with `description` field
- Descriptions are routing decisions — be specific, not vague
- Target 50-150 lines per file, 200 max
- 5-10 items per folder
- Subfolders need a folder descriptor (`<folder-name>.md`, frontmatter only)

## What to file

{prompt}
