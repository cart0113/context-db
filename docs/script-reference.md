# Script Reference

## build_toc.sh

Generates `<folder>_toc.md` files by walking context directories.

### Usage

```bash
bin/build_toc.sh                    # Rebuild changed TOC files
bin/build_toc.sh CONTEXT/           # Build one directory tree
bin/build_toc.sh --build-all        # Rebuild all TOC files unconditionally
```

### Behavior

- Finds root context nodes (directories with a description file whose parent has none)
- Recurses into subdirectories that have description files
- Reads symlinked folders for descriptions but never writes into them
- Skips underscore-prefixed and dot-prefixed names

### Requirements

Bash 3.2+, awk, find, stat — standard on macOS and Linux.

---

## format_md.py

Formats Markdown tables to fixed-width column alignment.

### Usage

```bash
python3 bin/format_md.py file.md           # Format in place
python3 bin/format_md.py file.md -o out    # Write to output
cat file.md | python3 bin/format_md.py -   # Stdin to stdout
```
