---
description:
  Why static -toc.md files were replaced with show_toc.sh that generates TOC on
  stdout — solves the cross-project symlink problem
---

# Dynamic TOC Generation

Static, committed `-toc.md` files were replaced with `bin/show_toc.sh`, a script
that generates the TOC for any context-db folder on the fly and prints it to
stdout.

## Problem

Static `-toc.md` files broke down with cross-project sharing:

1. You symlink external context into `context-db/` and `.gitignore` the symlink
2. `build_toc.sh` regenerates the parent TOC to include the symlinked folder
3. Now the committed TOC either includes entries only you have (broken for
   others) or excludes entries you have (your agent misses them)

There is no clean way to have a committed file reflect per-user symlinks.

## Solution

`bin/show_toc.sh` takes a context-db folder path and prints the TOC to stdout.
No files written, nothing to commit.

```bash
bin/show_toc.sh context-db/
# Prints the TOC for the root context-db folder

bin/show_toc.sh context-db/my-project/
# Prints the TOC for that subfolder
```

### Agent Interaction

The agent runs `bin/show_toc.sh context-db/` as its entry point, then
recursively calls it on subfolders as it navigates deeper — the same browsing
pattern as reading static files, but with a shell command instead of a file
read.

The output format is the same `## Subfolders` / `## Files` structure with
`description:` / `path:` entries that the old static files used.

### Why This Works with Agent Systems

Every major agent framework supports running shell commands and reading stdout:

- **Claude Code**: `Bash` tool
- **Cursor / Windsurf**: Terminal tool
- **Codex**: Shell execution
- **MCP servers**: Can wrap the script as a tool
- **Custom agents**: Subprocess execution is universal

A script that returns text on stdout is the simplest possible interface.

## What Changed

| Aspect                 | Before (static)       | After (dynamic)            |
| ---------------------- | --------------------- | -------------------------- |
| TOC retrieval          | Read `-toc.md` file   | Run `show_toc.sh <dir>`    |
| TOC storage            | Committed files       | None — generated on demand |
| Cross-project symlinks | TOC mismatch problem  | Just works                 |
| Pre-commit hook        | Regenerated TOC files | Not needed for TOCs        |
| Agent instructions     | "read this file"      | "run this command"         |
| Output format          | Same                  | Same                       |

## What Stayed the Same

- Folder structure, naming convention, `<foldername>.md` description files
- YAML frontmatter with `description` and `status` fields
- Documents are still plain markdown — agents read them directly
- `build_toc.sh` still available for projects that need static files on disk
  (e.g., static site generation)
