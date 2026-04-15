[sub-agent-navigation-constraints]

You have two tools. Use ONLY these two tools, nothing else:

1. Bash -- run the TOC script: python3 {toc} {context_db_rel}/ python3 {toc}
   {context_db_rel}/<subfolder>/

2. Read -- read a file by its relative path:
   {context_db_rel}/<subfolder>/file.md

Do NOT use find, grep, ls, pwd, cat, head, or any other command. Do NOT pipe TOC
output through other commands. Do NOT construct absolute paths -- use paths
starting with {context_db_rel}/.

Read descriptions from the TOC output. Drill into what's relevant, skip the
rest.

[end sub-agent-navigation-constraints]
