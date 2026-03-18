#!/usr/bin/env python3
"""
format_md.py — Format Markdown tables to fixed-width column alignment.

Finds every table block (consecutive lines starting with |) in a Markdown
file and rewrites each row so columns are padded to uniform widths. Handles
left, center, and right alignment markers in separator rows.

Usage:
    python3 bin/format_md.py <file.md>           Format a file in place
    python3 bin/format_md.py <file.md> -o out    Write to a different file
    cat file.md | python3 bin/format_md.py -     Read from stdin, write stdout
"""

import re
import sys
from pathlib import Path


def parse_row(line):
    line = line.strip().strip("|")
    return [cell.strip() for cell in line.split("|")]


def is_separator_row(cells):
    return all(re.fullmatch(r":?-+:?", cell) for cell in cells if cell)


def alignment_of(cell):
    if cell.startswith(":") and cell.endswith(":"):
        return "center"
    if cell.endswith(":"):
        return "right"
    return "left"


def pad(text, width, align):
    if align == "right":
        return text.rjust(width)
    if align == "center":
        return text.center(width)
    return text.ljust(width)


def format_table(lines):
    rows = [parse_row(line) for line in lines]
    if not rows:
        return lines

    num_cols = max(len(row) for row in rows)
    rows = [row + [""] * (num_cols - len(row)) for row in rows]

    col_widths = [max(max(len(row[c]) for row in rows), 3) for c in range(num_cols)]

    alignments = ["left"] * num_cols
    for row in rows:
        if is_separator_row(row):
            alignments = [alignment_of(cell) if cell else "left" for cell in row]
            break

    result = []
    for row in rows:
        if is_separator_row(row):
            cells = []
            for j, cell in enumerate(row):
                w = col_widths[j]
                a = alignments[j]
                if a == "center":
                    cells.append(":" + "-" * (w - 2) + ":")
                elif a == "right":
                    cells.append("-" * (w - 1) + ":")
                else:
                    cells.append("-" * w)
            result.append("| " + " | ".join(cells) + " |")
        else:
            cells = [
                pad(cell, col_widths[j], alignments[j]) for j, cell in enumerate(row)
            ]
            result.append("| " + " | ".join(cells) + " |")

    return result


def format_content(content):
    lines = content.splitlines()
    output = []
    table_buf = []

    for line in lines:
        if line.strip().startswith("|"):
            table_buf.append(line)
        else:
            if table_buf:
                output.extend(format_table(table_buf))
                table_buf = []
            output.append(line)

    if table_buf:
        output.extend(format_table(table_buf))

    result = "\n".join(output)
    if content.endswith("\n"):
        result += "\n"
    return result


def main():
    args = sys.argv[1:]

    if not args:
        print("Usage: format_md.py <file.md> [-o output.md]", file=sys.stderr)
        sys.exit(1)

    input_path = args[0]
    output_path = None

    if "-o" in args:
        idx = args.index("-o")
        output_path = args[idx + 1]

    if input_path == "-":
        content = sys.stdin.read()
    else:
        content = Path(input_path).read_text()

    formatted = format_content(content)

    if output_path:
        Path(output_path).write_text(formatted)
        print(f"Written: {output_path}")
    elif input_path == "-":
        sys.stdout.write(formatted)
    else:
        Path(input_path).write_text(formatted)
        print(f"Formatted: {input_path}")


if __name__ == "__main__":
    main()
