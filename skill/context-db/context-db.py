#!/usr/bin/env python3
"""
context-db.py — the one script behind the /context-db skill.

Commands the user invokes. Each prints instructions that the calling agent follows:

  prompt "<task>"         Look up what the knowledge base says about a task.
  update ["<learning>"]   Write down what was learned (--commit / --push to commit too).
  wip ["<instruction>"]   Bring the work-in-progress plans up to date.
  configure               Set up or repair context-db in this repository.

Helpers the agent runs when the instructions say to. They do the file work:

  init                    Write the config and create whatever is missing.
  index [folder]          Regenerate index.md files and check the format.

Layout (the file format is described in prompts/format.md):

  context-db/
    context-db.json             shared config, committed
    context-db.local.json       per-user overrides, gitignored
    context-db-on-markdown/     ON_PROMPT.md ON_UPDATE.md ON_WIP.md ON_CONFIGURE.md
    <project>-project/          the project folder: the only place commands write
    <anything-else>/            background folders: read-only

Each top-level folder is an Open Knowledge Format (OKF) bundle.

Requires Python 3.8+ and nothing outside the standard library.
"""

import argparse
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from urllib.parse import unquote

VERSION = "0.1"
OKF_VERSION = "0.2"
CONTEXT_DB = "context-db"
CONFIG_NAME = "context-db.json"
LOCAL_CONFIG_NAME = "context-db.local.json"
ON_DIR_NAME = "context-db-on-markdown"
CONFIG_KEYS = ("project", "python", "main_branch")
RESERVED_FILES = ("index.md", "log.md")
STATUSES = ("draft", "stable", "deprecated")
ON_COMMANDS = ("prompt", "update", "wip", "configure")
MAX_FILE_LINES = 200
MAX_FOLDER_ITEMS = 12
MIGRATION_GUIDE = (
    "https://github.com/cart0113/context-db/blob/v0.1/context-db/"
    "context-db-project/context-db-migrate-from-v0.0/context-db-migrate-from-v0.0.md"
)

SKILL_DIR = os.path.dirname(os.path.abspath(__file__))


# ── Agent-facing text ────────────────────────────────────────────────────────
# Short pieces of text the agent reads. The long instructions are the files in
# prompts/. Edit wording here or there, never inside the functions below.

NOT_CONFIGURED = """
context-db is not set up in this repository: `{config_path}` does not exist.

Tell the user, and offer to run `/context-db configure`. Do nothing else.
"""

NO_INSTRUCTION = """
No instruction was given. Ask the user what they want to work on.
"""

FOLDER_HAS_INDEX = """
start at `{index}`
"""

FOLDER_HAS_NO_INDEX = """
it has no `index.md`, so list the folder and read the frontmatter descriptions to find your way
"""

PROJECT_FOLDER_MISSING = """
- **Project folder** `{folder}/` does not exist. Tell the user to run `/context-db configure`.
"""

BROKEN_MOUNT = """
- **Background folder** `{folder}/` is a broken symlink. Ignore it.
"""

WIP_FOR_PROMPT = """
These files describe the work happening right now. Read the ones that bear on the
instruction{on_branch} before anything else.
"""

WIP_FOR_WIP = """
Read every one of these files now.
"""

WIP_EMPTY = """
`{wip_dir}/` holds no plans: no work in progress is recorded.
"""

NOTHING_TO_ADD = """
tell the user there is nothing to add and stop
"""

NOTHING_TO_ADD_BUT_COMMIT = """
say so, skip the rest of this section, and go straight to the Commit section
"""

THEN_PUSH = """
Then push the current branch to its remote.
"""

DO_NOT_PUSH = """
Do not push.
"""

NOT_A_GIT_REPO = """
Not a git repository, or git is unavailable. Judge what has landed from the files
themselves and ask the user when unsure.
"""

MAIN_BRANCH_MISSING = """
The configured main branch `{main}` does not exist in this repository, so there is
nothing to compare against. Tell the user to fix `main_branch` with
`/context-db configure`.
"""

V0_LAYOUT_FOUND = """
This repository still has the v0.0 layout ({leftovers}). Follow the migration
guide before step 2: {guide}
"""

PROJECT_DESCRIPTOR = """
---
type: Folder
description:
  Main project folder for this repo — knowledge specific to {name}.
---
"""

WIP_DESCRIPTOR = """
---
type: Folder
description:
  Current work in progress — plans for what is being built right now. Files
  here are deleted once the work lands.
---
"""


def text(template, **values):
    return template.strip().format(**values)


# ── Locations ────────────────────────────────────────────────────────────────
# Every path printed for the agent is relative to the agent's cwd.


def rel(path):
    return os.path.relpath(path)


def git(*args):
    """Run a git command; return stdout, or "" on any failure."""
    try:
        result = subprocess.run(
            ["git", *args],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=15,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    return result.stdout if result.returncode == 0 else ""


def find_repo_root():
    """The directory that holds (or should hold) context-db/."""
    if os.path.isdir(CONTEXT_DB):
        return os.getcwd()
    toplevel = git("rev-parse", "--show-toplevel").strip()
    if toplevel:
        return toplevel
    return os.getcwd()


def context_db_dir():
    return rel(os.path.join(find_repo_root(), CONTEXT_DB))


def script_command(python):
    script = rel(os.path.join(SKILL_DIR, "context-db.py"))
    return f"{python} {shlex.quote(script)}"


def read_text(path):
    with open(path, "r", encoding="utf-8-sig", errors="replace") as f:
        return f.read()


def write_text(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


# ── Config ───────────────────────────────────────────────────────────────────
# context-db.json is committed and shared. context-db.local.json is gitignored;
# any key it sets overrides the shared value for this user only.


def load_json(path):
    """Return (data, problem). The problem is None when the file is usable."""
    try:
        data = json.loads(read_text(path))
    except ValueError as error:
        return None, f"is not valid JSON ({error})"
    if not isinstance(data, dict):
        return None, "is not a JSON object"
    return data, None


def read_json(path):
    data, problem = load_json(path)
    if problem:
        sys.exit(f"Error: {path} {problem}. Fix it by hand, or delete it and run configure.")
    return data


def write_json(path, data):
    ordered = {key: data[key] for key in CONFIG_KEYS if key in data}
    ordered.update(data)
    write_text(path, json.dumps(ordered, indent=2) + "\n")


def load_config(cdb):
    """The shared config with user overrides applied, or None when there is no config."""
    shared_path = os.path.join(cdb, CONFIG_NAME)
    if not os.path.isfile(shared_path):
        return None
    config = read_json(shared_path)
    local_path = os.path.join(cdb, LOCAL_CONFIG_NAME)
    if os.path.isfile(local_path):
        config.update(read_json(local_path))
    missing = [key for key in CONFIG_KEYS if key not in config]
    if missing:
        sys.exit(f"Error: {shared_path} has no {', '.join(missing)}. Run /context-db configure.")
    return config


def require_config(cdb):
    config = load_config(cdb)
    if config is None:
        print(text(NOT_CONFIGURED, config_path=os.path.join(cdb, CONFIG_NAME)))
        sys.exit(0)
    return config


def project_dir(cdb, config):
    return os.path.join(cdb, f"{config['project']}-project")


# ── Frontmatter ──────────────────────────────────────────────────────────────
# Hand-rolled, because the skill must run on a bare interpreter with no PyYAML.
# It reads top-level scalar keys only, in every scalar style an LLM produces:
# inline, quoted, folded onto continuation lines, or behind a block indicator.
#
# Every key is optional as far as the parser is concerned, so callers read the
# result with .get(). Whether a key is required is lint's decision, not this
# parser's.

KEY_RE = re.compile(r"^([A-Za-z_][\w-]*):(?:\s+(.*))?$")
BLOCK_SCALAR_RE = re.compile(r"^[>|][-+0-9]*$")


def parse_frontmatter(content):
    """Return (meta, body). meta is None when there is no frontmatter block."""
    lines = content.split("\n")
    if lines[0].strip() != "---":
        return None, content
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return None, content

    meta = {}
    key = None
    for line in lines[1:end]:
        match = KEY_RE.match(line)
        if match:
            key = match.group(1)
            value = (match.group(2) or "").strip()
            meta[key] = "" if BLOCK_SCALAR_RE.match(value) else value
        elif key and line[:1] in (" ", "\t") and line.strip():
            meta[key] = (meta[key] + " " + line.strip()).strip()
    for key, value in meta.items():
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            meta[key] = value[1:-1]
    return meta, "\n".join(lines[end + 1 :])


def read_doc(path):
    return parse_frontmatter(read_text(path))


def strip_code(content):
    """Remove fenced code blocks and inline code so they are not scanned."""
    content = re.sub(r"(?ms)^[ \t]*(```|~~~).*?^[ \t]*\1[ \t]*$", "", content)
    return re.sub(r"`[^`\n]*`", "", content)


def doc_title(path, meta, body):
    """The frontmatter title, else the first H1, else the filename."""
    if meta.get("title"):
        return meta["title"]
    for line in strip_code(body).split("\n"):
        if line.startswith("# "):
            return line[2:].strip()
    return os.path.splitext(os.path.basename(path))[0]


def status_tag(meta):
    status = meta.get("status", "")
    return f" [{status}]" if status and status != "stable" else ""


# ── Walking a bundle ─────────────────────────────────────────────────────────
# A bundle is one top-level folder under context-db/. Symlinks inside it are
# never followed, and folders that hold no Markdown (images, scripts) are not
# part of the knowledge tree.


def visible(name):
    return not name.startswith(".")


def is_real_dir(path):
    return os.path.isdir(path) and not os.path.islink(path)


# Paths that git ignores, filled in by load_git_ignored() before a bundle is
# indexed. A committed index must list only what every clone has, so private,
# gitignored notes inside a bundle are left out of it.
GIT_IGNORED = set()


def load_git_ignored(bundle):
    GIT_IGNORED.clear()
    candidates = [bundle]
    for dirpath, dirnames, filenames in os.walk(bundle):
        dirnames[:] = [d for d in dirnames if visible(d)]
        candidates.extend(os.path.join(dirpath, name) for name in dirnames)
        candidates.extend(os.path.join(dirpath, name) for name in filenames if name.endswith(".md"))
    try:
        result = subprocess.run(
            ["git", "check-ignore", "--stdin"],
            check=False,
            input="\n".join(candidates) + "\n",
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=15,
        )
    except (OSError, subprocess.SubprocessError):
        return
    ignored = set(result.stdout.splitlines())
    if bundle not in ignored:  # a wholly private folder is indexed as it stands
        GIT_IGNORED.update(ignored)


def in_tree(folder, name):
    return visible(name) and os.path.join(folder, name) not in GIT_IGNORED


def folder_files(folder):
    """The folder's own documents: every visible .md except index.md and log.md."""
    return sorted(
        name
        for name in os.listdir(folder)
        if in_tree(folder, name)
        and name.endswith(".md")
        and name not in RESERVED_FILES
        and os.path.isfile(os.path.join(folder, name))
    )


def has_knowledge(folder):
    """True when the folder, or any real folder below it, holds a document."""
    if folder_files(folder):
        return True
    return any(
        has_knowledge(os.path.join(folder, name))
        for name in os.listdir(folder)
        if in_tree(folder, name) and is_real_dir(os.path.join(folder, name))
    )


def folder_subfolders(folder):
    return sorted(
        name
        for name in os.listdir(folder)
        if in_tree(folder, name)
        and is_real_dir(os.path.join(folder, name))
        and has_knowledge(os.path.join(folder, name))
    )


def bundle_folders(bundle):
    """Every folder of the knowledge tree, the bundle root first."""
    folders = [bundle]
    for name in folder_subfolders(bundle):
        folders.extend(bundle_folders(os.path.join(bundle, name)))
    return folders


def descriptor_path(folder):
    """A folder is described by <folder>/<folder>.md.

    A background folder may be symlinked under a different name than it has in
    the repository that owns it, so the real name is tried first.
    """
    for name in (os.path.basename(os.path.realpath(folder)), os.path.basename(folder)):
        candidate = os.path.join(folder, f"{name}.md")
        if os.path.isfile(candidate):
            return candidate
    return None


def folder_description(folder):
    path = descriptor_path(folder)
    if not path:
        return ""
    meta, _ = read_doc(path)
    return (meta or {}).get("description", "")


# ── Index generation ─────────────────────────────────────────────────────────
# index.md is OKF's progressive-disclosure file: one line per child, each with
# its description. It is derived entirely from frontmatter, so it is generated
# and never edited by hand.


def index_entry(title, target, description):
    title = title.replace("[", "\\[").replace("]", "\\]")
    line = f"* [{title}]({target})"
    return f"{line} - {description}" if description else line


def build_index(folder, is_root):
    descriptor = descriptor_path(folder)
    sub_lines = []
    for name in folder_subfolders(folder):
        description = folder_description(os.path.join(folder, name))
        sub_lines.append(index_entry(name, f"{name}/index.md", description))

    file_lines = []
    for name in folder_files(folder):
        path = os.path.join(folder, name)
        meta, body = read_doc(path)
        if descriptor and os.path.samefile(path, descriptor) and not body.strip():
            continue  # a frontmatter-only descriptor is shown by the parent's index
        meta = meta or {}
        description = (meta.get("description", "") + status_tag(meta)).strip()
        file_lines.append(index_entry(doc_title(path, meta, body), name, description))

    parts = []
    if is_root:
        parts.append(f'---\nokf_version: "{OKF_VERSION}"\n---')
    if sub_lines:
        parts.append("# Subfolders\n\n" + "\n".join(sub_lines))
    if file_lines:
        parts.append("# Files\n\n" + "\n".join(file_lines))
    return "\n\n".join(parts) + "\n"


def sync_indexes(bundle, check):
    """Write (or, with check, only compare) every index.md. Returns the stale paths."""
    stale = []
    for folder in bundle_folders(bundle):
        path = os.path.join(folder, "index.md")
        wanted = build_index(folder, folder == bundle)
        current = read_text(path) if os.path.isfile(path) else None
        if current == wanted:
            continue
        stale.append(path)
        if not check:
            write_text(path, wanted)
    return stale


# ── Lint ─────────────────────────────────────────────────────────────────────

LINK_RE = re.compile(r"\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")


def lint_links(path, body):
    problems = []
    for target in LINK_RE.findall(strip_code(body)):
        if SCHEME_RE.match(target) or target.startswith("#"):
            continue
        target = unquote(target.split("#")[0])
        if target.startswith("/"):
            problems.append(f"{path}: link `{target}` starts with / — make it relative to the file")
        elif not os.path.exists(os.path.join(os.path.dirname(path), target)):
            problems.append(f"{path}: broken link `{target}`")
    return problems


def lint_file(path, in_wip):
    errors, warnings = [], []
    content = read_text(path)
    meta, body = parse_frontmatter(content)
    if meta is None:
        return [f"{path}: no YAML frontmatter"], warnings
    for key in ("type", "description"):
        if not meta.get(key):
            errors.append(f"{path}: frontmatter has no `{key}`")
    status = meta.get("status", "")
    if status and status not in STATUSES:
        errors.append(f"{path}: status `{status}` is not one of {', '.join(STATUSES)}")
    errors.extend(lint_links(path, body))
    lines = content.count("\n")
    if lines > MAX_FILE_LINES and not in_wip:
        warnings.append(f"{path}: {lines} lines — split into a subfolder (max {MAX_FILE_LINES})")
    return errors, warnings


def lint_bundle(bundle):
    """Return (errors, warnings) for one bundle."""
    errors, warnings = [], []
    for dirpath, dirnames, filenames in os.walk(bundle):
        for name in sorted(dirnames):
            path = os.path.join(dirpath, name)
            if os.path.islink(path) and in_tree(dirpath, name):
                errors.append(
                    f"{path}: symlink inside a bundle — "
                    f"mount shared folders at the top level of {CONTEXT_DB}/ instead"
                )
        dirnames[:] = [d for d in dirnames if in_tree(dirpath, d)]
        if dirpath != bundle and "index.md" in filenames and not has_knowledge(dirpath):
            warnings.append(f"{dirpath}/: holds only an index.md — delete it")

    wip = os.path.join(bundle, "wip")
    for folder in bundle_folders(bundle):
        files = folder_files(folder)
        if not descriptor_path(folder):
            name = os.path.basename(os.path.realpath(folder))
            errors.append(f"{folder}/: no folder descriptor — add {name}.md with a description")
        items = len(files) + len(folder_subfolders(folder))
        if items > MAX_FOLDER_ITEMS:
            warnings.append(f"{folder}/: {items} items — split into subfolders (aim for 5–10)")
        in_wip = os.path.commonpath([wip, folder]) == wip
        for name in files:
            file_errors, file_warnings = lint_file(os.path.join(folder, name), in_wip)
            errors.extend(file_errors)
            warnings.extend(file_warnings)
    return errors, warnings


# ── Prompt composition ───────────────────────────────────────────────────────
# Each command prints a list of sections. Rules from the ON file come second to
# last and the user's instruction comes last, because recency wins.


def load_prompt(name, **values):
    """Load prompts/<name>.md and fill its {placeholders}."""
    content = read_text(os.path.join(SKILL_DIR, "prompts", f"{name}.md"))
    for key, value in values.items():
        content = content.replace("{" + key + "}", str(value))
    return content.strip()


def on_dir(cdb):
    return os.path.join(cdb, ON_DIR_NAME)


def on_file_text(cdb, command):
    """The body of ON_<COMMAND>.md with frontmatter and HTML comments removed."""
    path = os.path.join(on_dir(cdb), f"ON_{command.upper()}.md")
    if not os.path.isfile(path):
        return ""
    _, body = read_doc(path)
    return re.sub(r"(?s)<!--.*?-->", "", body).strip()


def emit(sections):
    print("\n\n".join(section for section in sections if section))


def instruction_of(args):
    return " ".join(args.instruction).strip()


def instruction_section(instruction):
    if not instruction:
        return ""
    return f"# User Instruction\n\n{instruction}"


def folders_section(cdb, config):
    """The project folder first, then every background folder.

    This list is generated on every call rather than committed, because a user
    may mount private folders through gitignored symlinks.
    """
    project = project_dir(cdb, config)
    lines = ["# Folders", ""]

    def entry(label, folder):
        description = folder_description(folder) or "(no description)"
        index = os.path.join(folder, "index.md")
        start = text(
            FOLDER_HAS_INDEX if os.path.isfile(index) else FOLDER_HAS_NO_INDEX, index=index
        )
        return f"- **{label}** `{folder}/` ({start}): {description}"

    if os.path.isdir(project):
        lines.append(entry("Project folder", project))
    else:
        lines.append(text(PROJECT_FOLDER_MISSING, folder=project))

    for name in sorted(os.listdir(cdb)):
        folder = os.path.join(cdb, name)
        if not visible(name) or name == ON_DIR_NAME or name == os.path.basename(project):
            continue
        if os.path.islink(folder) and not os.path.exists(folder):
            lines.append(text(BROKEN_MOUNT, folder=folder))
        elif os.path.isdir(folder):
            lines.append(entry("Background folder", folder))
    return "\n".join(lines)


def wip_files(wip):
    """(path, meta) for every plan under wip/, descriptors and indexes excluded."""
    found = []
    if not os.path.isdir(wip):
        return found
    for folder in bundle_folders(wip):
        descriptor = descriptor_path(folder)
        for name in folder_files(folder):
            path = os.path.join(folder, name)
            if descriptor and os.path.samefile(path, descriptor):
                continue
            meta, _ = read_doc(path)
            found.append((path, meta or {}))
    return found


def wip_section(cdb, config, intro):
    wip = os.path.join(project_dir(cdb, config), "wip")
    files = wip_files(wip)
    lines = ["# Work In Progress", ""]
    if not files:
        lines.append(text(WIP_EMPTY, wip_dir=wip))
        return "\n".join(lines)
    lines.extend([intro, ""])
    for path, meta in files:
        tags = status_tag(meta)
        if meta.get("branch"):
            tags += f" [branch: {meta['branch']}]"
        lines.append(f"- `{path}` — {meta.get('description') or '(no description)'}{tags}")
    return "\n".join(lines)


def current_branch():
    return git("rev-parse", "--abbrev-ref", "HEAD").strip()


def capped(output, limit):
    lines = output.rstrip().split("\n")
    if len(lines) <= limit:
        return "\n".join(lines)
    return "\n".join(lines[:limit]) + f"\n... ({len(lines) - limit} more lines)"


def git_state_section(config):
    branch = current_branch()
    if not branch:
        return "# Git State\n\n" + text(NOT_A_GIT_REPO)
    main = config["main_branch"]
    base = None
    for ref in (main, f"origin/{main}"):
        if git("rev-parse", "--verify", "--quiet", ref):
            base = ref
            break
    shown = "detached HEAD" if branch == "HEAD" else f"`{branch}`"
    lines = ["# Git State", "", f"- Current branch: {shown}", f"- Main branch: `{main}`"]

    def block(title, output, limit):
        output = output.strip("\n")
        body = capped(output, limit) if output else "(none)"
        lines.extend(["", f"## {title}", "", "```", body, "```"])

    block("Uncommitted changes (`git status --short`)", git("status", "--short"), 40)
    if base is None:
        lines.extend(["", text(MAIN_BRANCH_MISSING, main=main)])
        block("Recent commits", git("log", "--oneline", "-n", "15"), 15)
    elif branch == main:
        block("Recent commits", git("log", "--oneline", "-n", "15"), 15)
    else:
        block(
            f"Commits here that are not on `{main}`", git("log", "--oneline", f"{base}..HEAD"), 40
        )
        block(f"Files changed since `{main}`", git("diff", "--stat", f"{base}...HEAD"), 60)
    return "\n".join(lines)


# ── Commands ─────────────────────────────────────────────────────────────────


def cmd_prompt(args):
    cdb = context_db_dir()
    config = require_config(cdb)
    instruction = instruction_of(args)
    if not instruction:
        print(text(NO_INSTRUCTION))
        return
    branch = current_branch()
    on_branch = f" (the current branch is `{branch}`)" if branch else ""
    emit(
        [
            load_prompt("prompt", cdb=cdb, project_dir=project_dir(cdb, config)),
            folders_section(cdb, config),
            wip_section(cdb, config, text(WIP_FOR_PROMPT, on_branch=on_branch)),
            on_file_text(cdb, "prompt"),
            instruction_section(instruction),
        ]
    )


def cmd_update(args):
    cdb = context_db_dir()
    config = require_config(cdb)
    commit = args.commit or args.push
    sections = [
        load_prompt(
            "update",
            cdb=cdb,
            project_dir=project_dir(cdb, config),
            on_dir=on_dir(cdb),
            index_cmd=f"{script_command(config['python'])} index",
            nothing_to_add=text(NOTHING_TO_ADD_BUT_COMMIT if commit else NOTHING_TO_ADD),
        ),
        folders_section(cdb, config),
        load_prompt("format"),
    ]
    if commit:
        push = text(THEN_PUSH if args.push else DO_NOT_PUSH)
        sections.append(load_prompt("commit", cdb=cdb, push=push))
    sections.append(on_file_text(cdb, "update"))
    sections.append(instruction_section(instruction_of(args)))
    emit(sections)


def cmd_wip(args):
    cdb = context_db_dir()
    config = require_config(cdb)
    project = project_dir(cdb, config)
    emit(
        [
            load_prompt(
                "wip",
                project_dir=project,
                wip_dir=os.path.join(project, "wip"),
                branch=current_branch() or "<branch>",
                index_cmd=f"{script_command(config['python'])} index",
            ),
            git_state_section(config),
            wip_section(cdb, config, text(WIP_FOR_WIP)),
            load_prompt("format"),
            on_file_text(cdb, "wip"),
            instruction_section(instruction_of(args)),
        ]
    )


# ── configure and init ───────────────────────────────────────────────────────


def detect_main_branch():
    head = git("symbolic-ref", "--short", "refs/remotes/origin/HEAD").strip()
    if head.startswith("origin/"):
        return head[len("origin/") :]
    return current_branch() or "main"


def project_folders(cdb):
    """Names of the real <name>-project folders at the top level of context-db/."""
    if not os.path.isdir(cdb):
        return []
    return sorted(
        name
        for name in os.listdir(cdb)
        if name.endswith("-project") and is_real_dir(os.path.join(cdb, name))
    )


def suggest_project_name(root, cdb):
    found = project_folders(cdb)
    if len(found) == 1:
        return found[0][: -len("-project")], "the existing project folder"
    name = re.sub(r"[^a-z0-9]+", "-", os.path.basename(root).lower()).strip("-")
    return name or "my", "the repository name"


def python_version(executable):
    code = "import sys; print('.'.join(str(part) for part in sys.version_info[:3]))"
    try:
        result = subprocess.run(
            [executable, "-c", code],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=15,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    return result.stdout.strip()


def describe_python3():
    """How `python3` on PATH relates to the interpreter running this script."""
    found = shutil.which("python3")
    if not found:
        return "not found", False
    if os.path.realpath(found) == os.path.realpath(sys.executable):
        return "the interpreter running this script", True
    version = python_version(found)
    usable = tuple(int(part) for part in version.split(".")[:2]) >= (3, 8) if version else False
    verdict = "new enough" if usable else "too old; this script needs 3.8 or newer"
    return f"`{found}` (Python {version or 'unknown'}, {verdict})", usable


def v0_leftovers(root, cdb):
    """Signs that this repository still has the v0.0 layout."""
    found = []
    if os.path.isdir(cdb):
        found.extend(
            os.path.join(cdb, name)
            for name in sorted(os.listdir(cdb))
            if name.startswith("ON_") and name.endswith(".md")
        )
        found.extend(
            os.path.join(cdb, name, "wip.md")
            for name in project_folders(cdb)
            if os.path.isfile(os.path.join(cdb, name, "wip.md"))
        )
    old_scripts = os.path.join(root, ".claude", "skills", "context-db", "scripts")
    if os.path.isdir(old_scripts):
        found.append(rel(old_scripts) + "/")
    return found


def cmd_configure(args):
    root = find_repo_root()
    cdb = context_db_dir()
    version = ".".join(str(part) for part in sys.version_info[:3])
    python3, python3_usable = describe_python3()
    suggested_python = "python3" if python3_usable else sys.executable
    name, name_source = suggest_project_name(root, cdb)

    lines = ["# Detected State", ""]
    lines.append(f"- Interpreter running this script: `{sys.executable}` (Python {version})")
    lines.append(f"- `python3` on PATH: {python3}")
    lines.append(f"- Suggested `python` value: `{suggested_python}`")
    lines.append(f"- Repository root: `{rel(root)}/`")
    lines.append(f"- Suggested project name: `{name}` (from {name_source})")
    lines.append(f"- Detected main branch: `{detect_main_branch()}`")

    configured_python = None
    for label, filename in (("Shared config", CONFIG_NAME), ("User overrides", LOCAL_CONFIG_NAME)):
        path = os.path.join(cdb, filename)
        if not os.path.isfile(path):
            lines.append(f"- {label} `{path}`: does not exist")
            continue
        data, problem = load_json(path)
        if problem:
            lines.append(f"- {label} `{path}`: {problem}. Rewrite it by hand before step 2.")
            continue
        lines.append(f"- {label} `{path}`: `{json.dumps(data)}`")
        configured_python = data.get("python", configured_python)  # either file may omit it

    found = ", ".join(f"`{os.path.join(cdb, n)}/`" for n in project_folders(cdb)) or "none"
    lines.append(f"- Project folders found: {found}")
    state = "exists" if os.path.isdir(on_dir(cdb)) else "does not exist"
    lines.append(f"- ON files folder `{on_dir(cdb)}/`: {state}")
    leftovers = v0_leftovers(root, cdb)
    if leftovers:
        listed = ", ".join(f"`{path}`" for path in leftovers)
        lines.extend(["", text(V0_LAYOUT_FOUND, leftovers=listed, guide=MIGRATION_GUIDE)])

    emit(
        [
            load_prompt(
                "configure",
                cdb=cdb,
                config_name=CONFIG_NAME,
                local_config_name=LOCAL_CONFIG_NAME,
                init_cmd=f"{script_command(configured_python or suggested_python)} init",
                agents_snippet=rel(os.path.join(SKILL_DIR, "starters", "AGENTS.md")),
            ),
            "\n".join(lines),
            on_file_text(cdb, "configure"),
            instruction_section(instruction_of(args)),
        ]
    )


def write_if_missing(path, content, created):
    if os.path.exists(path):
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    write_text(path, content)
    created.append(path)


def ignore_local_config(root, cdb):
    """Make sure the per-user override file can never be committed."""
    local = os.path.join(cdb, LOCAL_CONFIG_NAME)
    if not git("rev-parse", "--show-toplevel") or git("check-ignore", local).strip():
        return False
    path = os.path.join(root, ".gitignore")
    existing = read_text(path) if os.path.isfile(path) else ""
    separator = "" if not existing or existing.endswith("\n") else "\n"
    write_text(path, f"{existing}{separator}{CONTEXT_DB}/{LOCAL_CONFIG_NAME}\n")
    return True


def check_project_name(cdb, name):
    if not name or name != name.strip() or re.search(r"[\s/\\]", name):
        sys.exit(f"Error: `{name}` is not a usable project name. Use something like acme-payments.")
    without_suffix = name[: -len("-project")]
    if (
        name.endswith("-project")
        and without_suffix
        and os.path.isdir(os.path.join(cdb, name))
        and not os.path.isdir(os.path.join(cdb, f"{name}-project"))
    ):
        sys.exit(
            f"Error: {os.path.join(cdb, name)}/ already exists, so the project name is "
            f"`{without_suffix}`. Pass --project {without_suffix}."
        )


def cmd_init(args):
    root = find_repo_root()
    cdb = context_db_dir()
    shared_path = os.path.join(cdb, CONFIG_NAME)
    local_path = os.path.join(cdb, LOCAL_CONFIG_NAME)

    config = read_json(shared_path) if os.path.isfile(shared_path) else {}
    previous_project = config.get("project")  # absent on the first run
    for key, value in (
        ("project", args.project),
        ("python", args.python),
        ("main_branch", args.main_branch),
    ):
        if value:
            config[key] = value
    if "project" not in config:
        sys.exit("Error: no project name. Pass --project <name>.")
    check_project_name(cdb, config["project"])
    if "python" not in config:
        config["python"] = "python3"
    if "main_branch" not in config:
        config["main_branch"] = detect_main_branch()

    local = None
    if args.local:
        local = read_json(local_path) if os.path.isfile(local_path) else {}
        for item in args.local:
            key, separator, value = item.partition("=")
            if not separator or not value or key not in CONFIG_KEYS:
                sys.exit(
                    f"Error: --local takes KEY=VALUE, where KEY is one of {', '.join(CONFIG_KEYS)}."
                )
            local[key] = value

    os.makedirs(cdb, exist_ok=True)
    write_json(shared_path, config)
    print(f"Wrote {shared_path}: {json.dumps(read_json(shared_path))}")
    if local is not None:
        write_json(local_path, local)
        print(f"Wrote {local_path}: {json.dumps(read_json(local_path))}")
    if ignore_local_config(root, cdb):
        print(f"Added {CONTEXT_DB}/{LOCAL_CONFIG_NAME} to .gitignore")

    name = config["project"]
    project = project_dir(cdb, config)
    if previous_project and previous_project != name:
        old = os.path.join(cdb, f"{previous_project}-project")
        if os.path.isdir(old):
            print(f"Note: the project folder is now {project}/. {old}/ is treated as background.")

    created = []
    starters = os.path.join(SKILL_DIR, "starters")
    for command in ON_COMMANDS:
        filename = f"ON_{command.upper()}.md"
        starter = read_text(os.path.join(starters, filename))
        write_if_missing(os.path.join(on_dir(cdb), filename), starter, created)
    write_if_missing(
        os.path.join(project, f"{name}-project.md"),
        text(PROJECT_DESCRIPTOR, name=name) + "\n",
        created,
    )
    write_if_missing(os.path.join(project, "wip", "wip.md"), text(WIP_DESCRIPTOR) + "\n", created)
    for path in created:
        print(f"Created {path}")
    print()
    sys.exit(run_index(project, check=False))


# ── index ────────────────────────────────────────────────────────────────────


def run_index(bundle, check):
    """Sync the indexes, print the lint report, and return the exit code."""
    load_git_ignored(bundle)
    stale = sync_indexes(bundle, check)
    errors, warnings = lint_bundle(bundle)
    if check:
        errors = [f"{path}: out of date — run the index command" for path in stale] + errors
    elif stale:
        print(f"Regenerated {len(stale)} index file(s):")
        for path in stale:
            print(f"  {path}")
    else:
        print("Index files are up to date.")
    for label, problems in (("ERROR", errors), ("WARNING", warnings)):
        for problem in problems:
            print(f"{label}: {problem}")
    if errors:
        print(f"\n{len(errors)} error(s). Fix them and run this command again.")
        return 1
    print(f"{bundle}/ is a conformant OKF v{OKF_VERSION} bundle.")
    return 0


def symlink_on_the_way(folder):
    """The first symlink in a relative path, or None."""
    if os.path.isabs(folder):
        return folder if os.path.islink(folder) else None
    path = ""
    for part in folder.split(os.sep):
        path = os.path.join(path, part)
        if os.path.islink(path):
            return path
    return None


def bundle_root(folder):
    """Climb from a folder to the top of the bundle it belongs to.

    Every folder inside a bundle has a descriptor, so the bundle root is the
    last folder on the way up whose parent has none.
    """
    while True:
        parent = os.path.dirname(os.path.abspath(folder))
        if parent == os.path.abspath(folder) or not descriptor_path(parent):
            return folder
        folder = rel(parent)


def cmd_index(args):
    if args.folder:
        folder = os.path.normpath(args.folder)
        if not os.path.isdir(folder):
            sys.exit(f"Error: {folder}/ is not a folder.")
        link = symlink_on_the_way(folder)
        if link:
            sys.exit(
                f"Error: {link} is a symlink to a folder owned elsewhere. "
                "Run index in the repository that owns it."
            )
        bundle = bundle_root(folder)
        if bundle != folder:
            print(f"{folder}/ is inside {bundle}/; indexing all of {bundle}/.")
    else:
        cdb = context_db_dir()
        bundle = project_dir(cdb, require_config(cdb))
        if not os.path.isdir(bundle):
            sys.exit(f"Error: {bundle}/ does not exist. Run /context-db configure.")
    sys.exit(run_index(bundle, args.check))


# ── CLI ──────────────────────────────────────────────────────────────────────


def build_parser():
    parser = argparse.ArgumentParser(
        prog="context-db",
        description="A Markdown knowledge base for coding agents, in Open Knowledge Format.",
    )
    parser.add_argument(
        "--version", action="version", version=f"context-db {VERSION} (OKF {OKF_VERSION})"
    )
    subs = parser.add_subparsers(dest="command", metavar="<command>")

    def instruction(sub):
        sub.add_argument("instruction", nargs="*", help="Free text; quote it as one argument")

    p = subs.add_parser("prompt", help="Look up what the knowledge base says about a task")
    instruction(p)

    p = subs.add_parser("update", help="Write down what was learned")
    instruction(p)
    p.add_argument("--commit", action="store_true", help="Then commit the whole session")
    p.add_argument("--push", action="store_true", help="Then commit and push")

    p = subs.add_parser("wip", help="Bring the work-in-progress plans up to date")
    instruction(p)

    p = subs.add_parser("configure", help="Set up or repair context-db in this repository")
    instruction(p)

    p = subs.add_parser("init", help="(helper) Write the config and create whatever is missing")
    p.add_argument("--project", help="Project name; its folder is context-db/<name>-project/")
    p.add_argument("--python", help="Interpreter command used to run this script")
    p.add_argument("--main-branch", help="Branch that work in progress is compared against")
    p.add_argument(
        "--local",
        action="append",
        metavar="KEY=VALUE",
        help=f"Per-user override, written to {LOCAL_CONFIG_NAME} (repeatable)",
    )

    p = subs.add_parser("index", help="(helper) Regenerate index.md files and check the format")
    p.add_argument("folder", nargs="?", default="", help="Default: the project folder")
    p.add_argument("--check", action="store_true", help="Change nothing; exit 1 on any problem")

    subs.add_parser("help", help="Show this help message")
    return parser


def main():
    # Output contains non-ASCII punctuation; never let a legacy locale crash it.
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8", errors="replace")
    parser = build_parser()
    args = parser.parse_args()
    handlers = {
        "prompt": cmd_prompt,
        "update": cmd_update,
        "wip": cmd_wip,
        "configure": cmd_configure,
        "init": cmd_init,
        "index": cmd_index,
    }
    if args.command not in handlers:
        parser.print_help()
        return
    handlers[args.command](args)


if __name__ == "__main__":
    main()
