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

# Matches YAML block scalar indicators: >, >-, >+, |, |-, |+, >2, etc.
# When a description value is one of these, the real content is on the next
# indented lines — so we treat the indicator line as "found but empty."
BLOCK_SCALAR_RE = re.compile(r"^[>|][-+0-9]*\s*$")


def read_field(filepath, field):
    """Read a YAML frontmatter field from a markdown file.

    Handles: single-line values, multi-line continuation, block scalar
    indicators (>, >-, >+, |, |-, |+, >2, etc.), quoted values, and
    fenced YAML fallback.

    This is a hand-rolled parser (no PyYAML dependency) because:
    1. stdlib-only — no pip install in the skill runtime
    2. We only need `description` and `status`, not full YAML
    3. LLMs produce every YAML scalar style; we must handle them all
    """
    try:
        with open(filepath, "r") as f:
            lines = f.readlines()
    except (OSError, UnicodeDecodeError):
        return ""

    # Try standard --- frontmatter first, fall back to ```yaml description fence
    val = _parse_frontmatter(lines, field)
    if not val:
        val = _parse_fenced_yaml(lines, field)
    return val


def _parse_frontmatter(lines, field):
    """Parse standard YAML frontmatter (between --- delimiters).

    State machine: track fence_count (0=before, 1=inside, 2=after) and
    found (whether we've seen our field and are collecting continuation lines).
    Multi-line values are joined with spaces (folded style).
    """
    fence_count = 0
    found = False
    val_parts = []

    for line in lines:
        stripped = line.rstrip("\n")

        # --- delimiter tracking
        if stripped == "---":
            fence_count += 1
            if fence_count == 1:
                continue  # opening fence
            if fence_count >= 2:  # closing fence
                if found:
                    return _clean_value(" ".join(val_parts))
                return ""

        if fence_count != 1:
            continue

        # Inside frontmatter — collecting continuation lines for our field
        if found:
            if line[0:1] in (" ", "\t"):  # indented = continuation
                val_parts.append(stripped.strip())
                continue
            # Non-indented = next field, stop collecting
            return _clean_value(" ".join(val_parts))

        # Look for the target field (e.g. "description:")
        if stripped.startswith(field + ":"):
            rest = stripped[len(field) + 1 :].strip()
            if BLOCK_SCALAR_RE.match(rest):
                # Block scalar indicator (>, |, >-, etc.) — skip it,
                # real content is on the next indented lines
                found = True
                continue
            if rest:
                return _clean_value(rest)  # inline value
            # Bare "field:" with nothing after — multi-line follows
            found = True

    # Hit EOF while still collecting (malformed but recoverable)
    if found:
        return _clean_value(" ".join(val_parts))
    return ""


def _parse_fenced_yaml(lines, field):
    """Fallback: parse YAML from ```yaml description fenced blocks.

    Some files use a ```yaml description code fence instead of ---
    frontmatter. Same parsing logic as _parse_frontmatter, just different
    delimiters.
    """
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


def generate_toc(directory, local_only=False):
    """Generate TOC for a directory. Returns the output string.

    If local_only=True, skip entries whose paths resolve outside the project
    root (external symlinks). Project root is discovered by walking up from
    the target directory.

    Output is YAML-ish list consumed by the LLM, not parsed by code.
    Two sections: ## Subfolders (dirs with <name>/<name>.md descriptor)
    and ## Files (standalone .md files with description frontmatter).
    """
    directory = directory.rstrip("/")

    if not os.path.isdir(directory):
        print(f"Error: '{directory}' is not a directory", file=sys.stderr)
        sys.exit(1)

    project_root = find_project_root(directory) if local_only else None
    # dirname used to identify the folder's own descriptor file (skip it)
    dirname = os.path.basename(os.path.realpath(directory))

    folder_lines = []
    try:
        entries = sorted(os.listdir(directory))
    except OSError:
        entries = []

    # ── Subfolders: only listed if they have a <name>/<name>.md descriptor ──
    for name in entries:
        subdir = os.path.join(directory, name)
        if not os.path.isdir(subdir):
            continue
        if should_skip(name):
            continue
        if local_only and not is_project_local(subdir, project_root):
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

    # ── Files: standalone .md files (not the folder descriptor itself) ──
    file_lines = []
    for name in entries:
        filepath = os.path.join(directory, name)
        if not os.path.isfile(filepath):
            continue
        if not name.endswith(".md"):
            continue
        if should_skip(name):
            continue
        if local_only and not is_project_local(filepath, project_root):
            continue
        if name == f"{dirname}.md":  # folder descriptor — already used above
            continue

        desc = read_desc(filepath)
        if not desc:
            continue

        status = read_status(filepath)
        if status and status != "stable":
            desc = f"{desc} [{status}]"

        file_lines.append(f"- description: {desc}")
        file_lines.append(f"  path: {name}")

    # Assemble output — matches the original bash script's format exactly
    parts = []
    if folder_lines:
        parts.append("## Subfolders\n\n" + "\n".join(folder_lines))
    if file_lines:
        parts.append("## Files\n\n" + "\n".join(file_lines))

    return "\n\n".join(parts) + "\n" if parts else ""


# ── Project root discovery and local-only filtering ──────────────────────────


def find_project_root(start_path):
    """Walk up from start_path looking for .git, context-db.json, or context-db/.

    Used by --no-external-symlinks to determine the boundary. Anything
    resolving outside this root is excluded from the TOC.
    """
    current = os.path.realpath(start_path)
    if os.path.isfile(current):
        current = os.path.dirname(current)
    while True:
        if (os.path.exists(os.path.join(current, ".git"))
                or os.path.exists(os.path.join(current, "context-db.json"))
                or os.path.isdir(os.path.join(current, "context-db"))):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            print("Error: could not find project root (.git, context-db.json, "
                  "or context-db/ directory)", file=sys.stderr)
            sys.exit(1)
        current = parent


def is_project_local(path, project_root):
    """Check if a path resolves to within the project root."""
    real = os.path.realpath(path)
    root = os.path.realpath(project_root)
    return real.startswith(root + os.sep) or real == root


# ── CLI ──────────────────────────────────────────────────────────────────────


def main():
    # Manual arg parsing (no argparse) to keep startup fast — this script
    # is called frequently by the agent during TOC browsing.
    if len(sys.argv) < 2:
        print("Usage: context-db-generate-toc.py [--no-external-symlinks] "
              "<directory>", file=sys.stderr)
        sys.exit(1)

    local_only = False
    args = sys.argv[1:]
    if "--no-external-symlinks" in args:
        local_only = True
        args.remove("--no-external-symlinks")

    if not args:
        print("Usage: context-db-generate-toc.py [--no-external-symlinks] "
              "<directory>", file=sys.stderr)
        sys.exit(1)

    output = generate_toc(args[0], local_only=local_only)
    if output:
        print(output, end="")


if __name__ == "__main__":
    main()
