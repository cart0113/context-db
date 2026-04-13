#!/usr/bin/env python3
"""
context-db-generate-toc.py — print table of contents for any folder.

Python port of context-db-generate-toc.sh. Same output format, same
frontmatter parsing.

Scans a directory for Markdown files with YAML frontmatter `description`
fields and prints them as a TOC.

Usage:
  context-db-generate-toc.py context-db/
  context-db-generate-toc.py context-db/some-folder/
  context-db-generate-toc.py --list-files context-db/

Output format:
  ## Subfolders
  - description: ...
    path: subfolder/

  ## Files
  - description: ...
    path: filename.md

Dependencies: python3 (stdlib only)
"""

import os
import re
import sys


# ── Frontmatter parsing ─────────────────────────────────────────────────────

BLOCK_SCALAR_RE = re.compile(r"^[>|][-+0-9]*\s*$")


def read_field(filepath, field):
    """Read a YAML frontmatter field from a markdown file.

    Handles: single-line values, multi-line continuation, block scalar
    indicators (>, >-, >+, |, |-, |+, >2, etc.), quoted values, and
    fenced YAML fallback.
    """
    try:
        with open(filepath, "r") as f:
            lines = f.readlines()
    except (OSError, UnicodeDecodeError):
        return ""

    val = _parse_frontmatter(lines, field)
    if not val:
        val = _parse_fenced_yaml(lines, field)
    return val


def _parse_frontmatter(lines, field):
    """Parse standard YAML frontmatter (between --- delimiters)."""
    fence_count = 0
    found = False
    val_parts = []

    for line in lines:
        stripped = line.rstrip("\n")

        if stripped == "---":
            fence_count += 1
            if fence_count == 1:
                continue
            if fence_count >= 2:
                if found:
                    return _clean_value(" ".join(val_parts))
                return ""

        if fence_count != 1:
            continue

        # Inside frontmatter
        if found:
            # Continuation line (indented)
            if line[0:1] in (" ", "\t"):
                val_parts.append(stripped.strip())
                continue
            # Non-indented line = next field, we're done
            return _clean_value(" ".join(val_parts))

        # Look for our field
        if stripped.startswith(field + ":"):
            rest = stripped[len(field) + 1 :].strip()
            # Block scalar indicator — treat as empty value, content follows
            if BLOCK_SCALAR_RE.match(rest):
                found = True
                continue
            if rest:
                return _clean_value(rest)
            # Empty value — content on next indented lines
            found = True

    # End of file while still collecting
    if found:
        return _clean_value(" ".join(val_parts))
    return ""


def _parse_fenced_yaml(lines, field):
    """Fallback: parse YAML from ```yaml description fenced blocks."""
    in_block = False
    found = False
    val_parts = []

    for line in lines:
        stripped = line.rstrip("\n")

        if stripped.startswith("```yaml description"):
            in_block = True
            continue
        if in_block and stripped.startswith("```"):
            if found:
                return _clean_value(" ".join(val_parts))
            return ""

        if not in_block:
            continue

        if found:
            if line[0:1] in (" ", "\t"):
                val_parts.append(stripped.strip())
                continue
            return _clean_value(" ".join(val_parts))

        if stripped.startswith(field + ":"):
            rest = stripped[len(field) + 1 :].strip()
            if BLOCK_SCALAR_RE.match(rest):
                found = True
                continue
            if rest:
                return _clean_value(rest)
            found = True

    if found:
        return _clean_value(" ".join(val_parts))
    return ""


def _clean_value(val):
    """Strip surrounding quotes from a value."""
    val = val.strip()
    if len(val) >= 2 and val[0] == val[-1] and val[0] in ("'", '"'):
        val = val[1:-1]
    return val


def read_desc(filepath):
    """Read the description field from frontmatter."""
    return read_field(filepath, "description")


def read_status(filepath):
    """Read the status field from frontmatter."""
    return read_field(filepath, "status")


def should_skip(name):
    """Skip hidden and underscore-prefixed entries."""
    return name.startswith("_") or name.startswith(".")


# ── TOC generation ───────────────────────────────────────────────────────────


def generate_toc(directory):
    """Generate TOC for a directory. Returns the output string."""
    directory = directory.rstrip("/")

    if not os.path.isdir(directory):
        print(f"Error: '{directory}' is not a directory", file=sys.stderr)
        sys.exit(1)

    dirname = os.path.basename(os.path.realpath(directory))

    # Subfolder entries
    folder_lines = []
    try:
        entries = sorted(os.listdir(directory))
    except OSError:
        entries = []

    for name in entries:
        subdir = os.path.join(directory, name)
        if not os.path.isdir(subdir):
            continue
        if should_skip(name):
            continue

        descriptor = os.path.join(subdir, f"{name}.md")
        if not os.path.isfile(descriptor):
            continue

        desc = read_desc(descriptor) or "(no description)"
        status = read_status(descriptor)
        if status and status != "stable":
            desc = f"{desc} [{status}]"

        folder_lines.append(f"- description: {desc}")
        folder_lines.append(f"  path: {name}/")

    # File entries
    file_lines = []
    for name in entries:
        filepath = os.path.join(directory, name)
        if not os.path.isfile(filepath):
            continue
        if not name.endswith(".md"):
            continue
        if should_skip(name):
            continue
        # Skip folder descriptor
        if name == f"{dirname}.md":
            continue

        desc = read_desc(filepath)
        if not desc:
            continue

        status = read_status(filepath)
        if status and status != "stable":
            desc = f"{desc} [{status}]"

        file_lines.append(f"- description: {desc}")
        file_lines.append(f"  path: {name}")

    # Output — match bash format: header, blank line, entries
    parts = []
    if folder_lines:
        parts.append("## Subfolders\n\n" + "\n".join(folder_lines))
    if file_lines:
        parts.append("## Files\n\n" + "\n".join(file_lines))

    return "\n\n".join(parts) + "\n" if parts else ""


# ── Project-local check (absorbs context-db-list-files.sh) ───────────────────


def is_project_local(path, project_root=None):
    """Check if a path resolves to within the project root.

    Used to skip symlinks pointing outside the project (they belong to
    another repo).
    """
    if project_root is None:
        project_root = os.getcwd()
    real = os.path.realpath(path)
    root = os.path.realpath(project_root)
    return real.startswith(root + os.sep) or real == root


# ── CLI ──────────────────────────────────────────────────────────────────────


def main():
    if len(sys.argv) < 2:
        print("Usage: context-db-generate-toc.py <directory>", file=sys.stderr)
        sys.exit(1)

    directory = sys.argv[1]
    output = generate_toc(directory)
    if output:
        print(output, end="")


if __name__ == "__main__":
    main()
