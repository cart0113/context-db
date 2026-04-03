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

- Finds root context nodes (directories with a description file whose parent has none)
- Recurses into subdirectories that have description files
- Reads symlinked folders for descriptions but never writes into them
- Skips underscore-prefixed and dot-prefixed names
- Never treats the project root as a context node

### Requirements

Bash 3.2+, awk, find, stat — standard on macOS and Linux.
