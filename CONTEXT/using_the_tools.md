---
title: Using the Tools
description: How to use build_toc.sh and format_md.py in your projects
---

# Using the Tools

## build_toc.sh

`bin/build_toc.sh` scans `CONTEXT/` directories and regenerates the auto-generated sections of every `CONTEXT_TOC.md` it finds.

### Running It

```bash
# From project root — finds and updates all CONTEXT_TOC.md files
bin/build_toc.sh

# Update a specific CONTEXT/ directory
bin/build_toc.sh path/to/CONTEXT/

# Update a specific CONTEXT_TOC.md
bin/build_toc.sh path/to/CONTEXT/CONTEXT_TOC.md
```

### What It Does

For each `CONTEXT_TOC.md` found:

1. Reads the `<!-- CONTEXT_CONFIG ... -->` block for `depth`, `skip_underscore`, and `ignore` settings
2. Scans the `CONTEXT/` directory for:
   - **Subfolders** that contain a `CONTEXT_TOC.md`
   - **Sibling project directories** (adjacent to the project root) that have a `CONTEXT/CONTEXT_TOC.md`
   - **`.md` files** directly in `CONTEXT/` (excluding `CONTEXT_TOC.md` and `SYSTEM.md`)
3. Extracts `title` and `description` from the front matter of each resource
4. Replaces the content between `<!-- CONTEXT_FOLDERS:START -->` / `<!-- CONTEXT_FOLDERS:END -->` and `<!-- CONTEXT_FILES:START -->` / `<!-- CONTEXT_FILES:END -->` markers

### Config Options

Set these inside the `<!-- CONTEXT_CONFIG ... -->` block in your `CONTEXT_TOC.md`:

| Option | Default | Description |
|--------|---------|-------------|
| `depth` | `1` | How many levels deep to scan (currently depth=1 is the only supported value) |
| `skip_underscore` | `true` | Skip files and folders whose names start with `_` |
| `ignore` | (empty) | Comma-separated list of file/folder names to skip |
| `eager_read` | (empty) | Comma-separated list of folders the LLM should always load (informational only) |

### Automation

Wire up the pre-commit hook so TOCs stay current automatically:

```bash
cp hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

Or call `build_toc.sh` from any file-watcher setup you already use.

## format_md.py

`bin/format_md.py` reformats Markdown tables so columns are aligned in fixed-width fonts. Useful for cleaning up LLM-generated tables.

### Running It

```bash
# Format a file in place
python3 bin/format_md.py docs/architecture.md

# Write formatted output to a new file
python3 bin/format_md.py docs/architecture.md -o docs/architecture_clean.md

# Read from stdin
cat docs/architecture.md | python3 bin/format_md.py -
```

### What It Does

Scans for Markdown table blocks (consecutive lines beginning with `|`), calculates the maximum width of each column, and rewrites every row with padded cells. The separator row (`|---|---|`) is also reformatted to match. Supports left, right, and center alignment markers (`:---`, `---:`, `:---:`).
