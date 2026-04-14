[write-mechanics]

`{context_db_rel}/` is this project's knowledge base. To see which folders and
files you can edit, use the TOC script with --no-external-symlinks:

python3 {toc} --no-external-symlinks {context_db_rel}/

This filters out symlinked folders from other repos. Only edit local files.

Drill into subfolders the same way — run the TOC script again on a subfolder to
see its contents, always with --no-external-symlinks.

[end write-mechanics]
