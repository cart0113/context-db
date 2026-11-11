# How to Navigate Context-db

Context-db has no index files to read. To see what a folder holds, run:

    {toc_cmd} <folder>

It reads the folder's files as they are now and prints one line for each file
and subfolder, with its description. This is context-db's dynamic index: the
listing is built every time it is asked for, from the files themselves, so it
is never out of date. Use it every time you look into a folder, now or later in
the session, instead of listing the folder or opening files to see what they
are.

- Start with the project folder and the other folders listed under Folders.
- Open a file only when its description says it bears directly on the task.
- Run `{toc_cmd}` on a subfolder only when its description does.
- Skip everything else. Reading widely dilutes what matters.
- Links inside a file are relative to that file.
