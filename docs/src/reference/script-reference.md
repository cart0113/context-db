# Script Reference

## build_toc.sh

Generates `<folder>-toc.md` files by walking context directories.

### Usage

```bash
bin/build_toc.sh                    # Rebuild changed TOC files
bin/build_toc.sh context-db/        # Build one directory tree
bin/build_toc.sh --build-all        # Rebuild all TOC files unconditionally
```

### Behavior

- Finds root context nodes (directories with a description file whose parent has
  none)
- Recurses into subdirectories that have description files
- Reads symlinked folders for descriptions but never writes into them
- Skips underscore-prefixed and dot-prefixed names
- Never treats the project root as a context node

### Requirements

Bash 3.2+, awk, find, stat — standard on macOS and Linux.

## build_site.sh

Generates a browsable Docsify site from a context-db directory.

### Usage

```bash
bin/build_site.sh <source_dir> <output_dir>
bin/build_site.sh --embed <source_dir> <output_dir>
bin/build_site.sh --template file.html <source_dir> <output_dir>
```

### Flags

| Flag         | Effect                                                           |
| ------------ | ---------------------------------------------------------------- |
| `--embed`    | Skip index.html / .nojekyll (for nesting under existing Docsify) |
| `--template` | Use a custom index.html instead of the default                   |

### Behavior

- Parses `-toc.md` files to build a sidebar
- Strips YAML frontmatter from content files
- Generates a `README.md` landing page per subfolder
- Produces a standalone Docsify site (or embeddable fragment with `--embed`)

## pre-commit hook

Auto-rebuilds TOCs before every commit. Install with:

```bash
cp hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

The hook also runs Prettier on staged Markdown/JS/CSS/YAML files and Ruff on
staged Python files.
