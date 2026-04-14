You are maintaining a project knowledge base at {context_db_rel}/. Your working
directory is the project root.

## Step 1: Understand what changed

Run: git diff to see what changes were made this session.

## Step 2: Navigate existing knowledge

Browse the knowledge base: Run: bash {toc} {context_db_rel}/ Drill into folders:
bash {toc} {context_db_rel}/<subfolder>/ Read files to understand what's already
documented.

## Step 3: Update the knowledge base

Using the developer's notes AND the git diff, update {context_db_rel}/:

- Edit existing files when they cover the topic.
- Create new files only for genuinely new topics.
- Use absolute paths for all file operations.

## What belongs in context-db

Only file what the project assets (code, configs, docs, etc.) can't tell you.
Ask: "Would removing this cause the next agent to make a mistake, even after
reading the project assets?" If not, skip it.

Good content: conventions, corrections from the user, pitfalls (ripple effects,
files that must change together but aren't linked by imports), design rationale
invisible in the code, domain knowledge specific to this project.

Bad content: code summaries, what exists, how it's structured, step-by-step
instructions, anything derivable in 30 seconds with ls/grep/read.

## File format

- Every .md file needs YAML frontmatter with `description` field.
- Descriptions are routing decisions — be specific, not vague.
- Target 50-150 lines per file, 200 max.
- 5-10 items per folder.
- Subfolders need a folder descriptor file (<folder-name>.md, frontmatter only).

When done, summarize what you changed and why.
