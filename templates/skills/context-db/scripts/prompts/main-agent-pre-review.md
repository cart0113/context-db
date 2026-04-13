Navigate the project's context-db knowledge base to find knowledge and standards
applicable to your planned changes. Follow what you find when making edits.

## How to navigate

`{context_db_rel}/` is a B-tree of markdown files. Browse with the TOC script:

python3 {toc} {context_db_rel}/

Every file and folder has a `description` in its YAML frontmatter. The TOC
script lists descriptions — use them to decide what to read and what to skip.
Drill into relevant topics, ignore the rest. Any topic is reachable in 2-3
navigation steps.

To drill into a subfolder: python3 {toc} {context_db_rel}/<subfolder>/ To read a
file: Read {context_db_rel}/<subfolder>/file.md

## What to look for

Knowledge and standards directly applicable to your planned changes — pitfalls,
conventions, coding standards, anything you would get wrong without seeing.

## Your plan

{prompt}
