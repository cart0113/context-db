[write-file-format]

Every `.md` file needs YAML frontmatter with a `description` field — this is the
routing decision agents use to decide whether to open the file. Be specific:
"scheduler execution flow, budget enforcement hook" not "Architecture overview."

Two types:

- Documents — frontmatter + body
- Folder descriptors — frontmatter only, named `<folder-name>.md`

Every subfolder needs a folder descriptor. The root `context-db/` does not.

Structure:

- 5-10 items per folder
- 50-150 lines per file, 200 max
- If a file exceeds 200 lines, split it into a subfolder with the same name

Status field (optional in frontmatter): `draft`, `stable` (default when
omitted), `deprecated`, `experiment`, `work-in-progress`, `refactor`.

After changes, run the TOC script to verify YAML frontmatter is correct:

python3 {toc} <sub-folder-that-was-altered>/

[end write-file-format]
