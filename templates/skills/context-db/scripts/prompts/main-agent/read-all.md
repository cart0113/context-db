# Read All

Read everything in `{target_path}` exhaustively — every file, every subfolder,
all the way down.

Use the TOC script to list each level:

    python3 {toc} {target_path}

For every file listed, read the whole file. For every subfolder listed, run the
TOC script on that subfolder and repeat — read all files, recurse into all
subfolders. Do not skip anything based on relevance; the goal is complete
coverage.

If `{context_db_rel}/general-standards/` exists and is at or under the target
path, read it first.
