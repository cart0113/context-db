# context-md — Bootstrap Text

Copy the relevant sections below into whatever file your agent reads on startup — `CONTEXT.md`, `AGENTS.md`, `.cursorrules`, a `.claude/rules/` file, or a system prompt. Adjust paths to match your project.

For multiple CONTEXT/ trees, add a `Read ...` line for each entry point in the same file.

---

## 1. Reading Context

Read `CONTEXT/CONTEXT_toc.md` to start. Each entry has a description and a path.
Use descriptions to decide relevance — skip what you don't need.

- `_toc.md` path → subfolder. Read that TOC and repeat.
- Otherwise → read the document.

## 2. Writing Descriptions

Every `.md` file needs YAML frontmatter with a `description`:

```yaml
---
description: One-line summary — what this covers and why you'd read it
---
```

**Folder markers:** `<foldername>.md` with only the frontmatter above (no body). This registers the folder as a context node.

**Content documents:** Frontmatter + markdown body.

**Descriptions are critical.** The TOC shows only descriptions — it's the only thing an agent sees when deciding whether to open a file. Write the most specific summary you can.

To have your agent write descriptions for files that don't have them yet:

> For each `.md` file in `CONTEXT/` that has no `description` in its YAML frontmatter, read the file and add a description that tells a reader whether they need it without opening it.

## 3. Rebuilding TOCs

After adding, removing, or editing context files, regenerate the TOC indexes:

```bash
bin/build_toc.sh               # rebuild changed TOCs
bin/build_toc.sh --build-all   # rebuild all TOCs unconditionally
```

A pre-commit hook is available to do this automatically:

```bash
cp hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```
