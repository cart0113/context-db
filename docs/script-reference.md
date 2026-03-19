# Script Reference

## build_toc.sh

Generates TOC files from `context.cfg` / `<folder>.md` configs and context document
front matter.

### Usage

```bash
bin/build_toc.sh                    # Build all
bin/build_toc.sh CONTEXT/           # Build one directory
bin/build_toc.sh --check            # Only rebuild if sources changed
```

### Behavior

- Finds root context nodes (directories containing `context.cfg`)
- Recurses into subdirectories containing `<foldername>.md`
- Skips symlinked directories (reads them for descriptions but never writes to them)
- With `--check`: compares file modification times, skips up-to-date TOCs

### Requirements

Bash 3.2+, awk, find, stat — all standard on macOS and Linux.

---

## format_md.py

Formats Markdown tables to fixed-width column alignment.

### Usage

```bash
python3 bin/format_md.py file.md           # Format in place
python3 bin/format_md.py file.md -o out    # Write to output
cat file.md | python3 bin/format_md.py -   # Stdin to stdout
```

### What it does

Finds consecutive lines starting with `|`, calculates max column widths, and
rewrites with consistent padding. Preserves alignment markers (`:---`, `---:`,
`:---:`).
