Review your recent changes against the project's context-db knowledge base. Run
git diff to see what changed, then check conventions.

## How to navigate context-db

`{context_db_rel}/` is a B-tree of markdown files. Browse with the TOC script:

python3 {toc} {context_db_rel}/

Drill into relevant topics to find applicable conventions and standards.

To drill into a subfolder: python3 {toc} {context_db_rel}/<subfolder>/ To read a
file: Read {context_db_rel}/<subfolder>/file.md

## Steps

1. Run: git diff
2. Navigate context-db for relevant conventions
3. Compare your changes against what you find
4. Fix real issues, use your judgment on edge cases

## Summary of changes

{prompt}
