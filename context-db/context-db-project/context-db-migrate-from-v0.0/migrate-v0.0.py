#!/usr/bin/env python3
"""
migrate-v0.0.py — the mechanical half of moving a context-db from v0.0 to v0.1.

    python3 migrate-v0.0.py <path-to>/context-db [--dry-run]

What it changes, in every real (non-symlinked) top-level folder:

  - adds a guessed `type:` to frontmatter that has none
  - maps the retired statuses (experiment, work-in-progress, refactor) to draft
  - turns backticked paths that name another note into Markdown links

And at the top level of context-db/:

  - moves ON_PROMPT.md, ON_UPDATE.md and ON_MAINTAIN.md into configuration/
  - moves <name>-project/wip.md to <name>-project/wip/current-work.md, listed
    in a new <name>-project/wip/wip.md

It then prints three lists: what it changed, the types it guessed, and what it
could not decide, including every mention of v0.0 machinery it found. The guide
next to this script says what to do with each.

Running it twice is safe: the second run changes nothing.

Requires Python 3.8+ and nothing outside the standard library.
"""

import argparse
import os
import re
import sys

ON_DIR = "configuration"
RETIRED_STATUSES = ("experiment", "work-in-progress", "refactor")
OLD_DESCRIPTOR_NAMES = ("SKILL.md", "CONTEXT.md", "AGENT.md", "AGENTS.md")
TYPE_GUESSES = (
    (r"research|landscape|theory|evidence", "Research"),
    (r"decision|rationale|why ", "Decision"),
    (r"standard|convention|style|naming|voice", "Convention"),
    (r"architecture|data.model|schema|design of", "Architecture"),
    (r"gotcha|pitfall|lesson|edge case", "Gotcha"),
    (r"plan|roadmap|work in progress|todo", "Plan"),
)
V0_MACHINERY_RE = re.compile(
    r"TOC script|context-db-generate-toc|context-db-resolve-path|context-db-main-agent"
    r"|/context-db read\b|_drafts/|-instructions\.md|templates/skills"
)
PATH_SPAN_RE = re.compile(r"`((?:\.\.?/)?[\w./-]+\.md)`")
LINK_RE = re.compile(r"(\[[^\]]*\])\(([^)\s]+)\)")
NOT_RELATIVE_RE = re.compile(r"^([A-Za-z][A-Za-z0-9+.-]*:|#|/)")
FENCE_RE = re.compile(r"^[ \t]*(```|~~~)")
WIP_DESCRIPTOR = """---
type: Folder
description:
  Work in progress, if the project records it. wip.md lists each effort, when
  it started, and where it stands. The plans sit next to it and are deleted
  once the work lands.
---

# Work in progress

- [Current work](current-work.md). Moved from the v0.0 wip.md; give it a start date and a status.
"""


def read(path):
    with open(path, "r", encoding="utf-8-sig", errors="replace") as f:
        return f.read()


def write(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def frontmatter_end(lines):
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
    if stem == "wip" and folder_name.endswith("-project"):
        return "Plan"  # the old single wip file, about to move into wip/
    haystack = (path + " " + header).lower()
    for pattern, type_name in TYPE_GUESSES:
        if re.search(pattern, haystack):
            return type_name
    return "Reference"


def linkify(path, lines, start, names):
    """Replace code spans that name another note with links to it.

    `./x.md` and `x.md` become links when the file is there. A bare name that is
    not beside this file is looked up in the whole folder tree and linked when
    exactly one note has that name. Anything else is left alone; a path that
    starts with ./ or ../ and leads nowhere is reported.
    """
    count = 0
    undecided = []
    in_fence = False
    here = os.path.dirname(path)

    def replace(match):
        nonlocal count
        target = match.group(1)
        if os.path.isfile(os.path.join(here, target)):
            count += 1
            return f"[{os.path.basename(target)}]({target})"
        if "/" not in target:
            found = names.get(target, [])
            if len(found) == 1:
                count += 1
                return f"[{target}]({os.path.relpath(found[0], here)})"
            if len(found) > 1:
                undecided.append(
                    f"`{target}` could be any of {', '.join(found)} — link the right one"
                )
        elif target.startswith("."):
            undecided.append(f"`{target}` does not resolve — fix it, unless it is only an example")
        return match.group(0)

    for i in range(start, len(lines)):
        if FENCE_RE.match(lines[i]):
            in_fence = not in_fence
        elif not in_fence:
            lines[i] = PATH_SPAN_RE.sub(replace, lines[i])
    return count, undecided


def report_machinery(path, lines, report):
    for number, line in enumerate(lines, start=1):
        for mention in sorted(set(V0_MACHINERY_RE.findall(line))):
            report["mentions"].append(f"{path}:{number}: `{mention}`")


def migrate_file(path, folder_name, names, dry_run, report):
    lines = read(path).split("\n")
    end = frontmatter_end(lines)
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

    count, undecided = linkify(path, lines, end + 1, names)
    if count:
        report["changed"].append(f"{path}: {count} backticked path(s) -> links")
    report["decide"].extend(f"{path}: {item}" for item in undecided)
    report_machinery(path, lines, report)

    if lines != original and not dry_run:
        write(path, "\n".join(lines))


def missing_descriptor(folder, names):
    """What to say about a folder that has no <folder>.md descriptor."""
    name = os.path.basename(folder)
    for old in [f"{name}-instructions.md", *OLD_DESCRIPTOR_NAMES]:
        if old in names:
            return f"{folder}/: rename {old} to {name}.md — it is the folder descriptor"
    return f"{folder}/: no folder descriptor {name}.md"


def walk(bundle):
    """Yield (folder, note filenames) for every real folder in a bundle."""
    for dirpath, dirnames, filenames in os.walk(bundle):
        dirnames[:] = sorted(
            name
            for name in dirnames
            if not name.startswith(".") and not os.path.islink(os.path.join(dirpath, name))
        )
        notes = sorted(
            name
            for name in filenames
            if name.endswith(".md") and name not in ("index.md", "log.md")
        )
        yield dirpath, notes


def migrate_bundle(bundle, dry_run, report):
    names = {}
    for folder, notes in walk(bundle):
        for name in notes:
            names.setdefault(name, []).append(os.path.join(folder, name))

    for dirpath, dirnames, _ in os.walk(bundle):
        for name in sorted(dirnames):
            full = os.path.join(dirpath, name)
            if name.startswith("_"):
                report["decide"].append(
                    f"{full}/: underscore folders are no longer hidden — move to wip/ or delete"
                )
            if os.path.islink(full):
                report["decide"].append(
                    f"{full}: symlink inside a folder — mount it at the top level instead"
                )

    for folder, notes in walk(bundle):
        folder_name = os.path.basename(folder)
        if notes and f"{folder_name}.md" not in notes:
            report["decide"].append(missing_descriptor(folder, notes))
        for name in notes:
            migrate_file(os.path.join(folder, name), folder_name, names, dry_run, report)


def rebase_links(path, old_dir):
    """Rewrite relative links in a file that has moved out of old_dir."""

    def replace(match):
        target = match.group(2)
        if NOT_RELATIVE_RE.match(target):
            return match.group(0)
        rebased = os.path.relpath(os.path.join(old_dir, target), os.path.dirname(path))
        return f"{match.group(1)}({rebased})"

    write(path, LINK_RE.sub(replace, read(path)))


def move(src, dst, dry_run, report):
    report["changed"].append(f"{src} -> {dst}")
    if dry_run:
        return
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    os.rename(src, dst)


def move_wip(folder, dry_run, report):
    """Turn <name>-project/wip.md into <name>-project/wip/current-work.md."""
    old_wip = os.path.join(folder, "wip.md")
    if not os.path.isfile(old_wip):
        return
    new_wip = os.path.join(folder, "wip", "current-work.md")
    descriptor = os.path.join(folder, "wip", "wip.md")
    move(old_wip, new_wip, dry_run, report)
    if dry_run:
        return
    rebase_links(new_wip, folder)
    if not os.path.exists(descriptor):
        write(descriptor, WIP_DESCRIPTOR)
        report["changed"].append(f"{descriptor}: created")


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("context_db", help="Path to the context-db/ folder")
    parser.add_argument("--dry-run", action="store_true", help="Report only; change nothing")
    args = parser.parse_args()
    cdb = os.path.normpath(args.context_db)
    if not os.path.isdir(cdb):
        sys.exit(f"Error: {cdb} is not a folder.")

    report = {"changed": [], "types": [], "decide": [], "mentions": []}

    for name in ("ON_PROMPT.md", "ON_UPDATE.md", "ON_MAINTAIN.md"):
        src = os.path.join(cdb, name)
        if os.path.isfile(src):
            move(src, os.path.join(cdb, ON_DIR, name), args.dry_run, report)
    on_dir = os.path.join(cdb, ON_DIR)
    if os.path.isdir(on_dir):
        for name in sorted(os.listdir(on_dir)):
            if name.endswith(".md"):
                path = os.path.join(on_dir, name)
                report_machinery(path, read(path).split("\n"), report)

    for name in sorted(os.listdir(cdb)):
        folder = os.path.join(cdb, name)
        if name.startswith(".") or name == ON_DIR or not os.path.isdir(folder):
            continue
        if os.path.islink(folder):
            report["decide"].append(
                f"{folder}: symlinked folder — run this script in the repository that owns it"
            )
            continue
        migrate_bundle(folder, args.dry_run, report)
        if name.endswith("-project"):
            move_wip(folder, args.dry_run, report)

    for title, key in (
        ("Changed", "changed"),
        ("Types guessed (review these)", "types"),
        ("Needs a decision", "decide"),
        ("Mentions of v0.0 machinery (rewrite or delete each)", "mentions"),
    ):
        print(f"## {title}\n")
        print("\n".join(f"- {line}" for line in report[key]) or "(nothing)")
        print()
    if args.dry_run:
        print("Dry run: nothing was written.")


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8", errors="replace")
    main()
