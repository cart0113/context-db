# context-md

A portable standard for hierarchically organizing context as Markdown files, with auto-generated tables of contents for progressive disclosure.

An LLM reads a lightweight `_toc.md` index, sees one-line descriptions of every subfolder and file, and fetches only what's relevant to the current task. Agents don't read the description files — they read the TOC, then fetch individual documents.

## Example

A payments service with shared coding and git standards (see `example/`):

```
acme_payments/
└── CONTEXT/
    ├── CONTEXT.md
    ├── CONTEXT_toc.md                    ← generated
    ├── _drafts/                          ← skipped (underscore prefix)
    │   └── migration_plan.md
    ├── acme_payments/
    │   ├── acme_payments.md
    │   ├── acme_payments_toc.md          ← generated
    │   ├── architecture.md
    │   └── api_reference.md
    ├── coding_standards/ → shared/...    ← symlink (read-only)
    │   ├── coding_standards.md
    │   ├── naming_conventions.md
    │   └── error_handling.md
    └── git_standards/ → shared/...       ← symlink (read-only)
        ├── git_standards.md
        ├── commit_messages.md
        └── branching.md
```

The generated root TOC (`CONTEXT_toc.md`):

```
## Subfolders

- description: Acme Payments — architecture, APIs, and data model
  path: acme_payments/acme_payments_toc.md
- description: Shared coding standards — naming, error handling, and testing conventions *(read-only)*
  path: coding_standards/coding_standards_toc.md
- description: Git workflow — branching strategy, commit messages, and PR conventions *(read-only)*
  path: git_standards/git_standards_toc.md
```

The LLM reads this TOC, decides which paths are relevant, and follows `_toc.md` paths deeper. Symlinked folders show *(read-only)*. `_drafts/` doesn't appear.

## Rules

1. **Description file.** A folder is a context node if it contains any of: `<folder_name>.md`, `CONTEXT.md`, `SKILL.md`, `AGENT.md`, or `AGENTS.md`. The file needs only YAML front matter with a `description` key.

2. **Context documents.** Individual `.md` files use the same format — YAML front matter with `description`. The description appears in the parent's `_toc.md`.

3. **TOC generation.** `bin/build_toc.sh` walks the directory tree and generates `<folder>_toc.md` for each context node. With `--check`, it only rebuilds when source files are newer than the existing TOC.

4. **Symlinks.** Symlinked folders appear in the parent's TOC marked *(read-only)*. The script never writes into a folder whose real path is outside the project root.

5. **Skipping.** Underscore-prefixed (`_drafts/`) and dot-prefixed (`.hidden/`) names are always skipped.

## File Format

Description file (`<folder>.md`) — only the description:

```markdown
---
description: Architecture decisions and coding conventions
---
```

Context document:

```markdown
---
description: Why build_toc.sh is pure bash rather than Python
---

(content)
```

## Building

```bash
bin/build_toc.sh                    # Build all _toc.md files
bin/build_toc.sh --check            # Only rebuild if sources changed
bin/build_toc.sh CONTEXT/           # Build from a specific directory
```

### Pre-commit hook

```bash
cp hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

## Agent Entry Point

The LLM needs to know context-md exists. The `bootstrap/` folder has a skill and system instructions — wire one into your agent:

**Skill** (Claude Code, Codex):
```bash
mkdir -p skills
ln -s /path/to/context-md/bootstrap/skill.md skills/context-md.md
```

**Cursor rule:**
```bash
mkdir -p .cursor/rules
cp /path/to/context-md/templates/cursor-rule.mdc .cursor/rules/context-md.mdc
```

### Why Not SKILL.md?

Skills are designed for *procedures* — filling them with background knowledge degrades skill performance and conflates "what to do" with "what to know."

context-md takes the good parts of skills (standard structure, portability via symlinks, front matter) and applies them to background knowledge. The hierarchical folder structure enables progressive disclosure — keeping token usage low and context focused.

**Skills** → *what to do* | **context-md** → *what to know*

## Tools

| Script | Description |
|--------|-------------|
| `bin/build_toc.sh` | Recursive TOC builder with change detection |
| `bin/format_md.py` | Format Markdown tables to fixed-width alignment |
| `hooks/pre-commit` | Git hook that runs `build_toc.sh --check` |

## Future

A `<folder_name>.cfg` system for per-folder configuration (ignore lists, symlink follow rules) is under consideration.

## License

MIT
