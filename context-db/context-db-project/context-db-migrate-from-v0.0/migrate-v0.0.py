#!/usr/bin/env python3
"""
migrate-v0.0.py — the mechanical half of moving a context-db from v0.0 to v0.1.

    python3 migrate-v0.0.py <path-to>/context-db [--dry-run]

What it changes, in every real (non-symlinked) top-level folder:

  - adds a guessed `type:` to frontmatter that has none
  - maps the retired statuses (experiment, work-in-progress, refactor) to draft
  - turns backticked relative paths that resolve to a file into Markdown links

And at the top level of context-db/:

  - moves ON_PROMPT.md and ON_UPDATE.md into context-db-on-markdown/
  - moves <name>-project/wip.md to <name>-project/wip/current-work.md

Everything it cannot decide is printed under "Needs a decision". The guessed
types are a starting point; the guide next to this script covers the rest.

Dependencies: python 3.8+, stdlib only.
"""

import argparse
import os
import re
import sys

ON_DIR = "context-db-on-markdown"
RETIRED_STATUSES = ("experiment", "work-in-progress", "refactor")
TYPE_GUESSES = (
    (r"decision|rationale|why ", "Decision"),
    (r"standard|convention|style|naming|voice", "Convention"),
    (r"architecture|data.model|schema|design of", "Architecture"),
    (r"gotcha|pitfall|lesson|edge case", "Gotcha"),
    (r"research|landscape|theory|evidence", "Research"),
    (r"plan|roadmap|work in progress|todo", "Plan"),
)
PATH_SPAN_RE = re.compile(r"`((?:\.\.?/)[\w./-]+\.md)`")
FENCE_RE = re.compile(r"^[ \t]*(```|~~~)")


def frontmatter_bounds(lines):
    """Index of the closing --- line, or None when there is no frontmatter."""
    if not lines or lines[0].strip() != "---":
        return None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return i
    return None


def guess_type(path, folder_name, header):
    stem = os.path.splitext(os.path.basename(path))[0]
    if stem == folder_name:
        return "Folder"
    haystack = (path + " " + header).lower()
    for pattern, type_name in TYPE_GUESSES:
        if re.search(pattern, haystack):
            return type_name
    return "Reference"


def linkify(path, lines, start):
    """Replace `./x.md` code spans with links when the target exists."""
    count = 0
    unresolved = []
    in_fence = False
    for i in range(start, len(lines)):
        if FENCE_RE.match(lines[i]):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        def replace(match):
            nonlocal count
            target = match.group(1)
            if os.path.exists(os.path.join(os.path.dirname(path), target)):
                count += 1
                return f"[{os.path.basename(target)}]({target})"
            unresolved.append(target)
            return match.group(0)

        lines[i] = PATH_SPAN_RE.sub(replace, lines[i])
    return count, unresolved


def migrate_file(path, folder_name, dry_run, report):
    with open(path, "r", encoding="utf-8") as f:
        lines = f.read().split("\n")
    end = frontmatter_bounds(lines)
    if end is None:
        report["decide"].append(f"{path}: no YAML frontmatter — add type and description by hand")
        return
    original = list(lines)
    header = "\n".join(lines[1:end])

    if not re.search(r"(?m)^type:", header):
        type_name = guess_type(path, folder_name, header)
        lines.insert(1, f"type: {type_name}")
        end += 1
        report["types"].append(f"{path}: type: {type_name}")
    if not re.search(r"(?m)^description:", header):
        report["decide"].append(f"{path}: no description")
    for i in range(1, end):
        match = re.match(r"^status:\s*(\S+)\s*$", lines[i])
        if match and match.group(1) in RETIRED_STATUSES:
            lines[i] = "status: draft"
            report["changed"].append(f"{path}: status {match.group(1)} -> draft")

    count, unresolved = linkify(path, lines, end + 1)
    if count:
        report["changed"].append(f"{path}: {count} backticked path(s) -> links")
    for target in unresolved:
        report["decide"].append(
            f"{path}: `{target}` does not resolve — fix it, unless it is only an example"
        )

    if lines != original and not dry_run:
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))


def migrate_bundle(bundle, dry_run, report):
    for dirpath, dirnames, filenames in os.walk(bundle):
        for name in list(dirnames):
            full = os.path.join(dirpath, name)
            if name.startswith("_"):
                report["decide"].append(
                    f"{full}/: underscore folders are no longer hidden — move to wip/ or delete"
                )
            if os.path.islink(full):
                report["decide"].append(
                    f"{full}: symlink inside a bundle — mount it at the top level instead"
                )
        dirnames[:] = sorted(
            d
            for d in dirnames
            if not d.startswith(".") and not os.path.islink(os.path.join(dirpath, d))
        )
        folder_name = os.path.basename(dirpath)
        mds = sorted(n for n in filenames if n.endswith(".md") and n not in ("index.md", "log.md"))
        if f"{folder_name}.md" not in mds:
            report["decide"].append(f"{dirpath}/: no folder descriptor {folder_name}.md")
        for name in mds:
            migrate_file(os.path.join(dirpath, name), folder_name, dry_run, report)


def rebase_links(path, old_dir):
    """Rewrite relative links in a file that moved out of old_dir."""
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    def replace(match):
        target = match.group(2)
        if re.match(r"^([A-Za-z][A-Za-z0-9+.-]*:|#|/)", target):
            return match.group(0)
        rebased = os.path.relpath(os.path.join(old_dir, target), os.path.dirname(path))
        return f"{match.group(1)}({rebased})"

    with open(path, "w", encoding="utf-8") as f:
        f.write(re.sub(r"(\[[^\]]*\])\(([^)\s]+)\)", replace, text))


def move(src, dst, dry_run, report):
    report["changed"].append(f"{src} -> {dst}")
    if dry_run:
        return
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    os.rename(src, dst)


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("context_db", help="Path to the context-db/ folder")
    parser.add_argument("--dry-run", action="store_true", help="Report only; change nothing")
    args = parser.parse_args()
    cdb = os.path.normpath(args.context_db)
    if not os.path.isdir(cdb):
        sys.exit(f"Error: {cdb} is not a folder.")

    report = {"changed": [], "types": [], "decide": []}

    for name in ("ON_PROMPT.md", "ON_UPDATE.md"):
        src = os.path.join(cdb, name)
        if os.path.isfile(src):
            move(src, os.path.join(cdb, ON_DIR, name), args.dry_run, report)
    if os.path.isfile(os.path.join(cdb, "ON_MAINTAIN.md")):
        report["decide"].append(
            f"{os.path.join(cdb, 'ON_MAINTAIN.md')}: maintain is gone — fold what still matters "
            f"into {ON_DIR}/ON_UPDATE.md, then delete it"
        )

    for name in sorted(os.listdir(cdb)):
        folder = os.path.join(cdb, name)
        if name.startswith(".") or name == ON_DIR or not os.path.isdir(folder):
            continue
        if os.path.islink(folder):
            report["decide"].append(
                f"{folder}: symlinked bundle — run this script in the repo that owns it"
            )
            continue
        migrate_bundle(folder, args.dry_run, report)
        old_wip = os.path.join(folder, "wip.md")
        if name.endswith("-project") and os.path.isfile(old_wip):
            new_wip = os.path.join(folder, "wip", "current-work.md")
            move(old_wip, new_wip, args.dry_run, report)
            if not args.dry_run:
                rebase_links(new_wip, folder)

    for title, key in (
        ("Changed", "changed"),
        ("Types guessed (review these)", "types"),
        ("Needs a decision", "decide"),
    ):
        print(f"## {title}\n")
        print("\n".join(f"- {line}" for line in report[key]) or "(nothing)")
        print()
    if args.dry_run:
        print("Dry run: nothing was written.")


if __name__ == "__main__":
    main()
