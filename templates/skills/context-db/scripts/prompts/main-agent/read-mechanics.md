[read-mechanics]

`{context_db_rel}/` is this project's knowledge base. Browse what's available
with the TOC script:

python3 {toc} {context_db_rel}/

The TOC script lists descriptions for every file and subfolder at that level.
Read descriptions and:

- If a file is relevant, read the whole file (by design, files are around ~100
  lines).
- If a subfolder seems relevant, run the TOC script again on that subfolder, and
  repeat this recursive process, reading all files and subfolders you think are
  relevant and necessary.

If `{context_db_rel}/general-standards/` exists, always read every file in it
before starting any task. These are global standards that apply to all work —
like a CLAUDE.md.

[end read-mechanics]
