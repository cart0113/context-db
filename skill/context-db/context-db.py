#!/usr/bin/env python3
"""
context-db.py — the one script behind the /context-db skill.

Commands the user invokes. Each prints instructions that the calling agent
follows; COMMAND_SUMMARIES below is the one-line description of each, shown by
--help and repeated word for word in the README and on the docs home page.

  prompt "<task>"         Before a task.
  update ["<learning>"]   After a task (--commit / --push to commit too).
  wip ["<instruction>"]   Optional (--list, --cleanup, --clear).
  configure               First, and whenever you like. With --project and the
                          other setting flags it writes the files itself.
  maintain ["<scope>"]    Now and then: tidy the knowledge base (--use-git-diff).

One step the agent runs whenever it looks into the knowledge base, and CI runs
with --check. It is not listed in --help:

  toc [folder]            List a folder's files and subfolders with their
                          descriptions, read from the files just now.
  toc --check [folder]    Check the format of the folder the given one is in.

There are no index.md files. OKF lets a folder carry one; context-db builds the
same listing on demand instead, so it can never be out of date.

Layout (the file format is described in prompts/format.md):

  context-db/
    configuration/              plain Markdown the agent or the script reads
      settings.md               project, python, main_branch; committed
      settings.local.md         per-user overrides; gitignored
      ON_PROMPT.md ...          rules added to each command (ON_UPDATE, ON_WIP, ON_CONFIGURE)
    <project>-project/          the project folder: the only place commands write
      wip/wip.md                optional list of the work in progress
    <anything-else>/            background folders: read-only

Each top-level folder is an Open Knowledge Format (OKF) bundle.

Requires Python 3.8+ and nothing outside the standard library.
"""

import argparse
import datetime
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
CONF_DIR_NAME = "configuration"
SETTINGS_NAME = "settings.md"
LOCAL_SETTINGS_NAME = "settings.local.md"
SETTINGS_KEYS = ("project", "python", "main_branch")
WIP_LIST_NAME = "wip.md"
RESERVED_FILES = ("index.md", "log.md")
STATUSES = ("draft", "stable", "deprecated")
ON_COMMANDS = ("prompt", "update", "wip", "configure", "maintain")
AGENT_NOTE_FILES = ("AGENTS.md", "CLAUDE.md")
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

COMMAND_SUMMARIES = {
    "prompt": """
Before a task. Looks up what the knowledge base says about it.
""",
    "update": """
After a task. Writes down what the next agent would need, if anything. --push
also commits and pushes.
""",
    "wip": """
Optional, for long work. Keeps a short list of the work in progress. --list,
--cleanup, --clear.
""",
    "configure": """
First, and whenever you like. Sets context-db up by asking a few questions;
edit the files by hand afterwards.
""",
    "maintain": """
Now and then. Removes what the code and its comments already say, fixes what
has drifted, and splits and reorganizes. --use-git-diff also reads the git
history for what has gone out of date.
""",
}

NO_HISTORY = """
Not a git repository, or git is unavailable, so there is no history to read.
Tell the user, and maintain the knowledge base without it.
"""

HISTORY_ROW = """
- `{path}`: last changed {date} ({commit}); {behind} commits to the project since
"""

HISTORY_LINKED = """
; linked files changed since: {files}
"""

HISTORY_NOT_COMMITTED = """
- `{path}`: not committed yet
"""

HISTORY_EMPTY = """
(The project folder holds no notes yet.)
"""

NOT_CONFIGURED = """
context-db is not set up in this repository: `{settings_path}` does not exist.

Tell the user, and offer to run `/context-db configure`. Do nothing else.
"""

NO_INSTRUCTION = """
No instruction was given. Ask the user what they want to work on.
"""

PROJECT_FOLDER_MISSING = """
- **Project folder** `{folder}/` does not exist. Tell the user to run `/context-db configure`.
"""

BROKEN_MOUNT = """
- **Background folder** `{folder}/` is a broken symlink. Ignore it.
"""

WIP_FOR_PROMPT = """
The work happening right now, from `{wip_list}`. Its links are relative to
`{wip_dir}/`. Open the plans that bear on the instruction{on_branch} before
anything else.
"""

WIP_LISTED = """
From `{wip_list}`. Its links are relative to `{wip_dir}/`.
"""

WIP_EMPTY = """
`{wip_list}` lists nothing: no work in progress is recorded.
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
nothing to compare against. Tell the user to fix `main_branch` in
`{settings_path}`.
"""

V0_LAYOUT_FOUND = """
This repository still has the v0.0 layout ({leftovers}). Follow the migration
guide before step 2: {guide}
"""

TOC_HEADING = """
# Contents of `{folder}/`

Read from its files just now. To look inside a subfolder, run `{toc_cmd} <subfolder>`.
"""

TOC_EMPTY = """
Nothing is in this folder yet.
"""

STRAY_INDEX = """
{path}: context-db lists folders on the fly with `toc`, so index.md files are not used — delete it
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
  Work in progress, if the project records it. wip.md lists each effort, when
  it started, and where it stands. The plans sit next to it and are deleted
  once the work lands.
---

# Work in progress

<!--
One line per effort, linking its plan. /context-db wip keeps this list.
Example:
- [Refund endpoint](refund-endpoint.md). Started 2026-11-02 on `feature/refunds`. Endpoint done, idempotency next.
-->
"""

SETTINGS_BODY = """
<!--
Settings for the context-db skills. Edit them by hand whenever you like.

- project: the project folder is context-db/<project>-project/.
- python: the command that runs the skills' script, Python 3.8 or newer.
- main_branch: the branch that `/context-db wip --cleanup` compares against.

settings.local.md in this folder, if it exists, overrides any of these for one
user. It is gitignored.
-->
"""

LOCAL_SETTINGS_BODY = """
<!--
Your own overrides of settings.md, for this machine only. This file is
gitignored.
-->
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


# ── Settings ─────────────────────────────────────────────────────────────────
# settings.md is committed and shared. settings.local.md is gitignored; any key
# it sets overrides the shared value for this user only. Both are Markdown with
# the settings as `key: value` lines in the frontmatter, so the user and the
# agent read them like any other file and the script parses them like any
# other frontmatter.


def conf_dir(cdb):
    return os.path.join(cdb, CONF_DIR_NAME)


def settings_path(cdb, local=False):
    return os.path.join(conf_dir(cdb), LOCAL_SETTINGS_NAME if local else SETTINGS_NAME)


def load_settings(path):
    """Return (values, problem). The problem is None when the file is usable."""
    meta, _ = read_doc(path)
    if meta is None:
        return None, "has no `---` block at the top holding the settings"
    return meta, None


def read_settings(path):
    values, problem = load_settings(path)
    if problem:
        sys.exit(f"Error: {path} {problem}. Fix it by hand, or delete it and run configure.")
    return values


def write_settings(path, values, default_body):
    """Rewrite the frontmatter of a settings file, keeping whatever body it has."""
    body = read_doc(path)[1] if os.path.isfile(path) else "\n" + text(default_body) + "\n"
    keys = [key for key in SETTINGS_KEYS if key in values]
    keys += [key for key in values if key not in SETTINGS_KEYS]
    header = "\n".join(f"{key}: {values[key]}" for key in keys)
    write_text(path, f"---\n{header}\n---\n{body}")


def load_config(cdb):
    """The shared settings with user overrides applied, or None when there are none."""
    shared_path = settings_path(cdb)
    if not os.path.isfile(shared_path):
        return None
    config = read_settings(shared_path)
    local_path = settings_path(cdb, local=True)
    if os.path.isfile(local_path):
        config.update(read_settings(local_path))
    missing = [key for key in SETTINGS_KEYS if not config.get(key)]  # frontmatter: all optional
    if missing:
        sys.exit(f"Error: {shared_path} has no {', '.join(missing)}. Run /context-db configure.")
    return config


def require_config(cdb):
    config = load_config(cdb)
    if config is None:
        print(text(NOT_CONFIGURED, settings_path=settings_path(cdb)))
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
        if len(value) >= 2 and value[0] == value[-1] == '"':
            meta[key] = value[1:-1].replace('\\"', '"').replace("\\\\", "\\")
        elif len(value) >= 2 and value[0] == value[-1] == "'":
            meta[key] = value[1:-1].replace("''", "'")
    return meta, "\n".join(lines[end + 1 :])


def read_doc(path):
    return parse_frontmatter(read_text(path))


# The parser above is forgiving, but OKF asks for frontmatter that a real YAML
# parser accepts. These checks catch what writers actually get wrong in the
# keys context-db reads, without needing a YAML library.

SCALAR_KEYS = ("type", "description", "status", "branch", "title")
PLAIN_START_RE = re.compile(r"^([\[\]{}#&*!|>%@`,]|[-?:](\s|$))")


def scalar_problem(lines):
    """Why a value would fail or change in a strict YAML parser, or None.

    `lines` is the value as written: the rest of the key's line, then each
    indented continuation line, all stripped.
    """
    if not lines or BLOCK_SCALAR_RE.match(lines[0]):
        return None  # empty, or a block scalar whose content YAML takes verbatim
    joined = " ".join(lines)
    quote = joined[0] if joined[0] in "\"'" else ""
    if quote == '"':
        closed = len(re.findall(r'(?<!\\)"', joined)) == 2 and joined.endswith('"')
        return None if closed else "its double quotes do not pair up"
    if quote == "'":
        closed = joined.endswith("'") and "'" not in joined[1:-1].replace("''", "")
        return None if closed and len(joined) > 1 else "its single quotes do not pair up"
    if PLAIN_START_RE.match(joined):
        return f"it starts with `{joined[0]}`"
    for line in lines:
        if ": " in line or line.endswith(":"):
            return "it contains a colon followed by a space or a line end"
        if " #" in line or line.startswith("#"):
            return "it contains ` #`, which starts a YAML comment"
    return None


def yaml_problems(content):
    """Problems a strict YAML parser would have with the keys context-db reads."""
    lines = content.split("\n")
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), len(lines))
    values = {}
    key = None
    problems = []
    for line in lines[1:end]:
        match = KEY_RE.match(line)
        if match:
            key = match.group(1)
            first = (match.group(2) or "").strip()
            values[key] = [first] if first else []
        elif key and line[:1] in (" ", "\t") and line.strip():
            indent = line[: len(line) - len(line.lstrip())]
            if "\t" in indent and key in SCALAR_KEYS:
                problems.append(f"`{key}` is indented with a tab")
            values[key].append(line.strip())
    for key in SCALAR_KEYS:
        problem = scalar_problem(values.get(key, []))  # any of these keys may be absent
        if problem:
            problems.append(
                f"`{key}` is not valid YAML as written ({problem}) — "
                "reword it, or wrap the whole value in double quotes"
            )
    return problems


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


def folder_files(folder):
    """The folder's own documents: every visible .md except index.md and log.md."""
    return sorted(
        name
        for name in os.listdir(folder)
        if visible(name)
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
        if visible(name) and is_real_dir(os.path.join(folder, name))
    )


def folder_subfolders(folder):
    return sorted(
        name
        for name in os.listdir(folder)
        if visible(name)
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


# ── Folder listings ──────────────────────────────────────────────────────────
# OKF's index.md is a progressive-disclosure file: one line per child, each with
# its description. context-db never writes one. `toc` prints the same listing
# from the frontmatter as it is at that moment, so there is nothing to keep in
# step and nothing to commit.


def toc_entry(title, target, description):
    title = title.replace("[", "\\[").replace("]", "\\]")
    line = f"* [{title}]({target})"
    return f"{line} - {description}" if description else line


def folder_listing(folder, toc_cmd):
    """The OKF index of a folder, built now. Paths are relative to the caller's cwd."""
    descriptor = descriptor_path(folder)
    sub_lines = []
    for name in folder_subfolders(folder):
        path = os.path.join(folder, name)
        sub_lines.append(toc_entry(name, f"{path}/", folder_description(path)))

    file_lines = []
    for name in folder_files(folder):
        path = os.path.join(folder, name)
        meta, body = read_doc(path)
        if descriptor and os.path.samefile(path, descriptor) and not body.strip():
            continue  # a frontmatter-only descriptor is shown by the parent's listing
        meta = meta or {}
        description = (meta.get("description", "") + status_tag(meta)).strip()
        file_lines.append(toc_entry(doc_title(path, meta, body), path, description))

    parts = [text(TOC_HEADING, folder=folder, toc_cmd=toc_cmd)]
    if sub_lines:
        parts.append("# Subfolders\n\n" + "\n".join(sub_lines))
    if file_lines:
        parts.append("# Files\n\n" + "\n".join(file_lines))
    if not sub_lines and not file_lines:
        parts.append(text(TOC_EMPTY))
    return "\n\n".join(parts)


# ── Lint ─────────────────────────────────────────────────────────────────────

LINK_RE = re.compile(r"\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")


def lint_links(path, body):
    problems = []
    for target in LINK_RE.findall(strip_code(without_comments(body))):
        if SCHEME_RE.match(target) or target.startswith("#"):
            continue
        target = unquote(target.split("#")[0])
        if target.startswith("/"):
            problems.append(f"{path}: link `{target}` starts with / — make it relative to the file")
        elif not os.path.exists(os.path.join(os.path.dirname(path), target)):
            problems.append(f"{path}: broken link `{target}`")
    return problems


def unlisted_wip(wip):
    """Plans in wip/ that wip/wip.md does not link to."""
    list_path = os.path.join(wip, WIP_LIST_NAME)
    if not os.path.isfile(list_path):
        return []
    _, body = read_doc(list_path)
    listed = {
        os.path.normpath(unquote(target.split("#")[0])).split(os.sep)[0]
        for target in LINK_RE.findall(strip_code(without_comments(body)))
    }
    items = [name for name in folder_files(wip) if name != WIP_LIST_NAME]
    items += folder_subfolders(wip)
    return [
        f"{os.path.join(wip, name)}: not listed in {list_path} — add a line for it"
        for name in sorted(items)
        if name not in listed
    ]


def lint_file(path, in_wip):
    errors, warnings = [], []
    content = read_text(path)
    meta, body = parse_frontmatter(content)
    if meta is None:
        return [f"{path}: no YAML frontmatter"], warnings
    for key in ("type", "description"):
        if not meta.get(key):
            errors.append(f"{path}: frontmatter has no `{key}`")
    errors.extend(f"{path}: {problem}" for problem in yaml_problems(content))
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
            if os.path.islink(path) and visible(name):
                errors.append(
                    f"{path}: symlink inside a bundle — "
                    f"mount shared folders at the top level of {CONTEXT_DB}/ instead"
                )
        dirnames[:] = [d for d in dirnames if visible(d)]
        if "index.md" in filenames:
            errors.append(text(STRAY_INDEX, path=os.path.join(dirpath, "index.md")))

    wip = os.path.join(bundle, "wip")
    if is_real_dir(wip):
        warnings.extend(unlisted_wip(wip))
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


def navigate_section(config):
    """How to look into the knowledge base: run toc, never read an index file."""
    return load_prompt("navigate", toc_cmd=f"{script_command(config['python'])} toc")


def load_prompt(name, **values):
    """Load prompts/<name>.md and fill its {placeholders}."""
    content = read_text(os.path.join(SKILL_DIR, "prompts", f"{name}.md"))
    for key, value in values.items():
        content = content.replace("{" + key + "}", str(value))
    return content.strip()


def without_comments(content):
    return re.sub(r"(?s)<!--.*?-->", "", content).strip()


def on_file_text(cdb, command):
    """The body of ON_<COMMAND>.md with frontmatter and HTML comments removed."""
    path = os.path.join(conf_dir(cdb), f"ON_{command.upper()}.md")
    if not os.path.isfile(path):
        return ""
    _, body = read_doc(path)
    rules = without_comments(body)
    if rules and not rules.startswith("#"):
        rules = f"# Project Rules\n\n{rules}"
    return rules


def emit(sections):
    print("\n\n".join(section for section in sections if section))


def instruction_of(args):
    """The user's instruction. A lone `-` means: read it from standard input."""
    if args.instruction == ["-"]:
        return sys.stdin.read().strip()
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
        return f"- **{label}** `{folder}/`: {description}"

    if os.path.isdir(project):
        lines.append(entry("Project folder", project))
    else:
        lines.append(text(PROJECT_FOLDER_MISSING, folder=project))

    for name in sorted(os.listdir(cdb)):
        folder = os.path.join(cdb, name)
        if not visible(name) or name == CONF_DIR_NAME or name == os.path.basename(project):
            continue
        if os.path.islink(folder) and not os.path.exists(folder):
            lines.append(text(BROKEN_MOUNT, folder=folder))
        elif os.path.isdir(folder):
            lines.append(entry("Background folder", folder))
    return "\n".join(lines)


def wip_dir(cdb, config):
    return os.path.join(project_dir(cdb, config), "wip")


def wip_list_path(cdb, config):
    return os.path.join(wip_dir(cdb, config), WIP_LIST_NAME)


def wip_list(cdb, config):
    """The list in wip/wip.md, without its frontmatter, comments, or headings.

    Empty when the file is missing or lists nothing, which is how a project
    that does not use wip/ looks.
    """
    path = wip_list_path(cdb, config)
    if not os.path.isfile(path):
        return ""
    _, body = read_doc(path)
    lines = [line for line in without_comments(body).split("\n") if not line.startswith("#")]
    items = "\n".join(lines).strip()
    return items if re.search(r"(?m)^\s*([-*+]|\d+\.)\s", items) else ""


def wip_section(cdb, config, intro, show_empty, **values):
    """The list of work in progress. When it is empty, "" unless show_empty."""
    items = wip_list(cdb, config)
    names = dict(wip_list=wip_list_path(cdb, config), wip_dir=wip_dir(cdb, config), **values)
    if not items:
        return "# Work In Progress\n\n" + text(WIP_EMPTY, **names) if show_empty else ""
    return f"# Work In Progress\n\n{text(intro, **names)}\n\n{items}"


def current_branch():
    return git("rev-parse", "--abbrev-ref", "HEAD").strip()


def capped(output, limit):
    lines = output.rstrip().split("\n")
    if len(lines) <= limit:
        return "\n".join(lines)
    return "\n".join(lines[:limit]) + f"\n... ({len(lines) - limit} more lines)"


def git_state_section(cdb, config):
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
        lines.extend(["", text(MAIN_BRANCH_MISSING, main=main, settings_path=settings_path(cdb))])
        block("Recent commits", git("log", "--oneline", "-n", "15"), 15)
    elif branch == main:
        block("Recent commits", git("log", "--oneline", "-n", "15"), 15)
    else:
        block(
            f"Commits here that are not on `{main}`", git("log", "--oneline", f"{base}..HEAD"), 40
        )
        block(f"Files changed since `{main}`", git("diff", "--stat", f"{base}...HEAD"), 60)
    return "\n".join(lines)


# The history behind `maintain --use-git-diff`: for each note, how far the
# project has moved since the note last changed.

MAX_HISTORY_NOTES = 60
OUTSIDE_CONTEXT_DB = (":/", f":(top,exclude){CONTEXT_DB}")


def project_notes(bundle):
    """Every note in the project folder outside wip/, descriptors with a body included."""
    wip = os.path.join(bundle, "wip")
    notes = []
    for folder in bundle_folders(bundle):
        if os.path.commonpath([wip, folder]) == wip:
            continue
        descriptor = descriptor_path(folder)
        for name in folder_files(folder):
            path = os.path.join(folder, name)
            body = read_doc(path)[1]
            if descriptor and os.path.samefile(path, descriptor) and not body.strip():
                continue
            notes.append((path, body))
    return notes


def linked_project_files(cdb, path, body):
    """The files outside context-db/ that a note links to and that exist."""
    found = []
    top = os.path.abspath(cdb)
    for target in LINK_RE.findall(strip_code(without_comments(body))):
        if SCHEME_RE.match(target) or target.startswith(("#", "/")):
            continue
        linked = os.path.normpath(
            os.path.join(os.path.dirname(path), unquote(target.split("#")[0]))
        )
        if os.path.exists(linked) and os.path.commonpath([top, os.path.abspath(linked)]) != top:
            found.append(linked)
    return sorted(set(found))


def git_history_section(cdb, config):
    """Each note against the commits made outside context-db/ since it last changed."""
    if not current_branch():
        return "# Git History\n\n" + text(NO_HISTORY)
    rows = []  # (linked files changed, commits behind, line), most out of date sorts first
    for path, body in project_notes(project_dir(cdb, config)):
        last = git("log", "-1", "--format=%h %as", "--", path).split()
        if not last:
            rows.append((False, -1, text(HISTORY_NOT_COMMITTED, path=path)))
            continue
        commit, date = last
        behind = int(git("rev-list", "--count", f"{commit}..HEAD", "--", *OUTSIDE_CONTEXT_DB) or 0)
        line = text(HISTORY_ROW, path=path, date=date, commit=commit, behind=behind)
        linked = linked_project_files(cdb, path, body)
        changed = (
            git("diff", "--name-only", f"{commit}..HEAD", "--", *linked).split() if linked else []
        )
        if changed:
            line += text(HISTORY_LINKED, files=", ".join(f"`{name}`" for name in changed))
        rows.append((bool(changed), behind, line))
    rows.sort(key=lambda row: (row[0], row[1]), reverse=True)
    lines = [load_prompt("maintain-git", cdb=cdb), ""]
    lines.extend(line for _, _, line in rows[:MAX_HISTORY_NOTES])
    if len(rows) > MAX_HISTORY_NOTES:
        lines.append(f"- ... ({len(rows) - MAX_HISTORY_NOTES} more notes)")
    if not rows:
        lines.append(text(HISTORY_EMPTY))
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
            navigate_section(config),
            load_prompt("not-a-mirror"),
            wip_section(cdb, config, WIP_FOR_PROMPT, show_empty=False, on_branch=on_branch),
            folders_section(cdb, config),
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
            conf_dir=conf_dir(cdb),
            wip_dir=wip_dir(cdb, config),
            toc_cmd=f"{script_command(config['python'])} toc",
            check_cmd=f"{script_command(config['python'])} toc --check",
            nothing_to_add=text(NOTHING_TO_ADD_BUT_COMMIT if commit else NOTHING_TO_ADD),
        ),
        load_prompt("not-a-mirror"),
        navigate_section(config),
        folders_section(cdb, config),
        load_prompt("format"),
    ]
    if commit:
        push = text(THEN_PUSH if args.push else DO_NOT_PUSH)
        sections.append(load_prompt("commit", cdb=cdb, push=push))
    sections.append(on_file_text(cdb, "update"))
    sections.append(instruction_section(instruction_of(args)))
    emit(sections)


def cmd_maintain(args):
    cdb = context_db_dir()
    config = require_config(cdb)
    emit(
        [
            load_prompt(
                "maintain",
                cdb=cdb,
                project_dir=project_dir(cdb, config),
                wip_dir=wip_dir(cdb, config),
                toc_cmd=f"{script_command(config['python'])} toc",
                check_cmd=f"{script_command(config['python'])} toc --check",
            ),
            load_prompt("not-a-mirror"),
            navigate_section(config),
            git_history_section(cdb, config) if args.use_git_diff else "",
            folders_section(cdb, config),
            load_prompt("format"),
            on_file_text(cdb, "maintain"),
            instruction_section(instruction_of(args)),
        ]
    )


def cmd_wip(args):
    """Record the current work, or with a flag: list, clean up, or clear it all."""
    cdb = context_db_dir()
    config = require_config(cdb)
    mode = "list" if args.list else "cleanup" if args.cleanup else "clear" if args.clear else ""
    values = {
        "project_dir": project_dir(cdb, config),
        "wip_dir": wip_dir(cdb, config),
        "wip_list": wip_list_path(cdb, config),
        "branch": current_branch() or "<branch>",
        "main": config["main_branch"],
        "today": datetime.date.today().isoformat(),
        "toc_cmd": f"{script_command(config['python'])} toc",
        "check_cmd": f"{script_command(config['python'])} toc --check",
    }
    sections = [load_prompt(f"wip-{mode}" if mode else "wip", **values)]
    if mode == "cleanup":
        sections.append(git_state_section(cdb, config))
    sections.append(wip_section(cdb, config, WIP_LISTED, show_empty=True))
    if mode != "list":
        sections.append(load_prompt("wip-format", **values))
    if mode in ("", "cleanup"):
        sections.append(load_prompt("not-a-mirror"))
        sections.append(navigate_section(config))
    if mode in ("", "cleanup"):
        sections.append(load_prompt("format"))
    sections.append(on_file_text(cdb, "wip"))
    sections.append(instruction_section(instruction_of(args)))
    emit(sections)


# ── configure ───────────────────────────────────────────────────────────────


def detect_main_branch():
    """Return (branch, how it was found). Only origin's default branch is certain."""
    head = git("symbolic-ref", "--short", "refs/remotes/origin/HEAD").strip()
    if head.startswith("origin/"):
        return head[len("origin/") :], "origin's default branch"
    branch = current_branch()
    if branch and branch != "HEAD":
        return branch, "a guess: the branch checked out now, because no remote names a default"
    return "main", "a guess: nothing could be detected"


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


def current_rules_section(cdb):
    """What each ON file tells the agent today, for configure to show the user."""
    lines = ["# Current Rules", ""]
    for command in ON_COMMANDS:
        path = os.path.join(conf_dir(cdb), f"ON_{command.upper()}.md")
        if not os.path.isfile(path):
            lines.append(f"## `{path}` (does not exist yet; setting up creates it)")
            continue
        _, body = read_doc(path)
        rules = without_comments(body)
        lines.extend([f"## `{path}`, added to every `/context-db {command}`", ""])
        lines.extend([rules or "(empty: it adds nothing)", ""])
    return "\n".join(lines).rstrip()


def cmd_configure(args):
    if wants_setup(args):
        cmd_setup(args)
        return
    root = find_repo_root()
    cdb = context_db_dir()
    version = ".".join(str(part) for part in sys.version_info[:3])
    python3, python3_usable = describe_python3()
    suggested_python = "python3" if python3_usable else sys.executable
    name, name_source = suggest_project_name(root, cdb)
    main_branch, main_branch_source = detect_main_branch()

    lines = ["# Detected State", ""]
    lines.append(f"- Interpreter running this script: `{sys.executable}` (Python {version})")
    lines.append(f"- `python3` on PATH: {python3}")
    lines.append(f"- Suggested `python` value: `{suggested_python}`")
    lines.append(f"- Repository root: `{rel(root)}/`")
    lines.append(f"- Suggested project name: `{name}` (from {name_source})")
    lines.append(f"- Suggested main branch: `{main_branch}` ({main_branch_source})")

    for label, local in (("Shared settings", False), ("Your own settings", True)):
        path = settings_path(cdb, local)
        if not os.path.isfile(path):
            lines.append(f"- {label} `{path}`: does not exist")
            continue
        values, problem = load_settings(path)
        if problem:
            lines.append(f"- {label} `{path}`: {problem}. Rewrite it by hand first.")
            continue
        shown = ", ".join(f"`{key}: {value}`" for key, value in values.items()) or "empty"
        lines.append(f"- {label} `{path}`: {shown}")

    found = ", ".join(f"`{os.path.join(cdb, n)}/`" for n in project_folders(cdb)) or "none"
    lines.append(f"- Project folders found: {found}")
    for note in AGENT_NOTE_FILES:
        path = os.path.join(root, note)
        if not os.path.isfile(path):
            lines.append(f"- `{rel(path)}`: does not exist")
        else:
            says = "mentions" if CONTEXT_DB in read_text(path) else "does not mention"
            lines.append(f"- `{rel(path)}`: exists, {says} `{CONTEXT_DB}/`")
    leftovers = v0_leftovers(root, cdb)
    if leftovers:
        listed = ", ".join(f"`{path}`" for path in leftovers)
        lines.extend(["", text(V0_LAYOUT_FOUND, leftovers=listed, guide=MIGRATION_GUIDE)])

    python = configured_python(cdb, default=suggested_python)
    emit(
        [
            load_prompt(
                "configure",
                cdb=cdb,
                conf_dir=conf_dir(cdb),
                settings=settings_path(cdb),
                local_settings=settings_path(cdb, local=True),
                setup_cmd=f"{script_command(python)} configure",
                toc_cmd=f"{script_command(python)} toc",
                check_cmd=f"{script_command(python)} toc --check",
                update_cmd=f"{script_command(python)} update",
                agents_snippet=rel(os.path.join(SKILL_DIR, "starters", "AGENTS.md")),
            ),
            "\n".join(lines),
            current_rules_section(cdb),
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


def ignore_local_settings(root, cdb):
    """Make sure the per-user settings file can never be committed. Returns the line added."""
    if not git("rev-parse", "--show-toplevel") or git("check-ignore", settings_path(cdb, True)):
        return ""
    line = f"{CONTEXT_DB}/{CONF_DIR_NAME}/{LOCAL_SETTINGS_NAME}"
    path = os.path.join(root, ".gitignore")
    existing = read_text(path) if os.path.isfile(path) else ""
    separator = "" if not existing or existing.endswith("\n") else "\n"
    write_text(path, f"{existing}{separator}{line}\n")
    return line


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


def wants_setup(args):
    """configure writes the files itself when any setting is passed."""
    return bool(args.project or args.python or args.main_branch or args.local)


def cmd_setup(args):
    """Write the settings and create whatever is missing. Never overwrites a file."""
    root = find_repo_root()
    cdb = context_db_dir()
    shared_path = settings_path(cdb)
    local_path = settings_path(cdb, local=True)

    config = read_settings(shared_path) if os.path.isfile(shared_path) else {}
    previous_project = config.get("project")  # frontmatter: absent on the first run
    for key, value in (
        ("project", args.project),
        ("python", args.python),
        ("main_branch", args.main_branch),
    ):
        if value:
            config[key] = value
    if not config.get("project"):
        sys.exit("Error: no project name. Pass --project <name>.")
    check_project_name(cdb, config["project"])
    config.setdefault("python", "python3")
    config.setdefault("main_branch", detect_main_branch()[0])

    local = None
    if args.local:
        local = read_settings(local_path) if os.path.isfile(local_path) else {}
        for item in args.local:
            key, separator, value = item.partition("=")
            if not separator or not value or key not in SETTINGS_KEYS:
                sys.exit(
                    "Error: --local takes KEY=VALUE, where KEY is one of "
                    f"{', '.join(SETTINGS_KEYS)}."
                )
            local[key] = value

    os.makedirs(conf_dir(cdb), exist_ok=True)
    write_settings(shared_path, config, SETTINGS_BODY)
    print(f"Wrote {shared_path}")
    if local is not None:
        write_settings(local_path, local, LOCAL_SETTINGS_BODY)
        print(f"Wrote {local_path}")
    ignored = ignore_local_settings(root, cdb)
    if ignored:
        print(f"Added {ignored} to .gitignore")

    name = config["project"]
    project = project_dir(cdb, config)
    if previous_project and previous_project != name:
        old = os.path.join(cdb, f"{previous_project}-project")
        if os.path.isdir(old):
            print(f"Note: the project folder is now {project}/. {old}/ is treated as background.")

    # The starters may name the command that runs this script; fill it in once,
    # with the shared interpreter, because the ON files are committed.
    python = config["python"]
    created = []
    starters = os.path.join(SKILL_DIR, "starters")
    for command in ON_COMMANDS:
        filename = f"ON_{command.upper()}.md"
        starter = read_text(os.path.join(starters, filename))
        starter = starter.replace("{update_cmd}", f"{script_command(python)} update")
        write_if_missing(os.path.join(conf_dir(cdb), filename), starter, created)
    write_if_missing(
        os.path.join(project, f"{name}-project.md"),
        text(PROJECT_DESCRIPTOR, name=name) + "\n",
        created,
    )
    write_if_missing(wip_list_path(cdb, config), text(WIP_DESCRIPTOR) + "\n", created)
    for path in created:
        print(f"Created {path}")
    print()
    rerun = f"{script_command(config['python'])} toc --check"
    sys.exit(run_check(project, rerun))


# ── toc ──────────────────────────────────────────────────────────────────────


def run_check(bundle, rerun):
    """Print the format report for a bundle and return the exit code.

    `rerun` is the command to print for checking again.
    """
    errors, warnings = lint_bundle(bundle)
    for label, problems in (("ERROR", errors), ("WARNING", warnings)):
        for problem in problems:
            print(f"{label}: {problem}")
    if errors:
        print(f"\n{len(errors)} error(s). Fix them, then run:  {rerun}")
        return 1
    print(f"{bundle}/ is a conformant OKF v{OKF_VERSION} bundle.")
    return 0


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


def configured_python(cdb, default="python3"):
    """The `python` setting if it can be read, else the default. Never fails."""
    python = default
    for local in (False, True):
        path = settings_path(cdb, local)
        values = load_settings(path)[0] if os.path.isfile(path) else None
        if values and values.get("python"):  # frontmatter: either file may leave it out
            python = values["python"]
    return python


def cmd_toc(args):
    cdb = context_db_dir()
    toc_cmd = f"{script_command(configured_python(cdb))} toc"
    if args.folder:
        folder = os.path.normpath(args.folder)
        if not os.path.isdir(folder):
            sys.exit(f"Error: {folder}/ is not a folder.")
    else:
        folder = project_dir(cdb, require_config(cdb))
        if not os.path.isdir(folder):
            sys.exit(f"Error: {folder}/ does not exist. Run /context-db configure.")
    if not args.check:
        print(folder_listing(folder, toc_cmd))
        return
    bundle = bundle_root(folder)
    if bundle != folder:
        print(f"{folder}/ is inside {bundle}/; checking all of {bundle}/.")
    rerun = f"{toc_cmd} --check" + (f" {shlex.quote(bundle)}" if args.folder else "")
    sys.exit(run_check(bundle, rerun))


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

    def command(name):
        summary = text(COMMAND_SUMMARIES[name])
        sub = subs.add_parser(name, help=summary, description=summary)
        sub.add_argument(
            "instruction",
            nargs="*",
            help="Free text, as one single-quoted argument; or `-` to read it from stdin",
        )
        return sub

    command("prompt")

    p = command("update")
    p.add_argument("--commit", action="store_true", help="Then commit the whole session")
    p.add_argument("--push", action="store_true", help="Then commit and push")

    p = command("wip")
    modes = p.add_mutually_exclusive_group()
    modes.add_argument(
        "--list", action="store_true", help="Show what is in progress; change nothing"
    )
    modes.add_argument(
        "--cleanup", action="store_true", help="Delete the plans for work that has landed"
    )
    modes.add_argument("--clear", action="store_true", help="Delete every plan, after asking")

    p = command("configure")
    setting = p.add_argument_group(
        "settings", "Pass any of these to write the files directly, with no questions asked"
    )
    setting.add_argument("--project", help="Project name; its folder is context-db/<name>-project/")
    setting.add_argument("--python", help="Command that runs this script (Python 3.8 or newer)")
    setting.add_argument("--main-branch", help="Branch that wip --cleanup compares against")
    setting.add_argument(
        "--local",
        action="append",
        metavar="KEY=VALUE",
        help=f"Per-user override, written to {LOCAL_SETTINGS_NAME} (repeatable)",
    )

    p = command("maintain")
    p.add_argument(
        "--use-git-diff",
        action="store_true",
        help="Also list each note against the commits made to the project since it changed",
    )

    # Left out of --help on purpose (no help= keyword): the agent runs it, and CI.
    p = subs.add_parser(
        "toc",
        description="List a folder's files and subfolders with their descriptions, "
        "read from the files now. With --check, check the format instead.",
    )
    p.add_argument("folder", nargs="?", default="", help="Default: the project folder")
    p.add_argument("--check", action="store_true", help="Check the format; exit 1 on any error")
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
        "maintain": cmd_maintain,
        "toc": cmd_toc,
    }
    if args.command not in handlers:
        parser.print_help()
        return
    handlers[args.command](args)


if __name__ == "__main__":
    main()
