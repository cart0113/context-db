## Writing to context-db

After completing a task, update context-db only if you encountered something
that would mislead the next agent — a non-obvious dependency, a constraint
invisible in the code, a convention the agent wouldn't know, or a correction
from the user. Do not summarize what the code does.

Update existing files when they cover the topic. Create new files only for
genuinely new pitfalls or conventions. Delete content that has drifted into code
summary. A smaller, accurate context-db outperforms a larger, comprehensive one.

### File format

Every `.md` file needs YAML frontmatter with a `description` field — this is the
routing decision agents use to decide whether to open the file. Be specific:
"scheduler execution flow, budget enforcement hook" not "Architecture overview."

Two types:

- **Documents** — frontmatter + body
- **Folder descriptors** — frontmatter only, named `<folder-name>.md`

Every subfolder needs a folder descriptor. The root `context-db/` does not.

### Structure

- 5-10 items per folder
- 50-150 lines per file, 200 max
- If a file exceeds 200 lines, split it into a subfolder with the same name
- 2-3 navigation steps to reach any topic (B-tree)

### Status field

Optional `status` field in frontmatter. Values: `draft`, `stable` (default when
omitted), `deprecated`, `experiment`, `work-in-progress`, `refactor`. Non-stable
status is shown in the TOC as `[status]`.

### After changes

Run the TOC script to verify YAML frontmatter is correct:

```
python3 {toc} {context_db_rel}/
```
