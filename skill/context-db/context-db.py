#!/usr/bin/env python3
"""
context-db.py — the one script behind the /context-db skill.

Commands the user invokes. Each prints instructions that the calling agent
follows; COMMAND_SUMMARIES below is the one-line description of each, shown by
--help and repeated word for word in the README and on the docs home page.

  prompt "<prompt>"       Before a question or task.
  update ["<steering>"]   After a task, from what the session learned
                          (--commit / --push to commit too).
  wip ["<what>"]          During long work: record where it stands (--list,
                          --maintain, --clear).
  maintain ["<scope>"]    Rarely: a spring cleaning of the whole knowledge base,
                          checked against the code and the git history.
  configure               First, and whenever you like. With --project and the
                          other setting flags it writes the files itself.

configure is listed last wherever the commands are listed: here, in --help, and
in the docs.

No flag narrows what prompt, update, or maintain look at. Each covers all of
the project's knowledge, and the user narrows or changes that in words, in the
instruction. The commands are a starting point for a conversation.

API below is what the user types. --help prints it, and the README and the
docs home page repeat it. It leaves out update's --commit and --push on
purpose: they are a convenience, a matter of preference, so only `update
--help` and the Commands page describe them.

Every one of them takes --show-context: print the same message, wrapped so that
the agent shows it to the user and does not act on it.

One step the agent runs whenever it looks into the knowledge base, and CI runs
with --check. It is not listed in --help:

  toc [folder]            List a folder's files and subfolders with their
                          descriptions, read from the files just now.
  toc --check [folder]    Check the format of the folder the given one is in.

OKF lets a folder carry an index.md. context-db needs none: it builds the same
listing on demand, so it can never be out of date. A project may keep index.md
files all the same, by hand or with a commit hook, for people and for other OKF
tools. In the folders the commands write, `toc` still lists from the files, and
`toc --check` warns when an index.md has fallen out of step with its folder. A
folder owned elsewhere that comes with an index.md is listed from it.

Layout (the file format is described in prompts/format.md):

  context-db/
    configuration/              plain Markdown the agent or the script reads
      settings.md               the settings (SETTINGS_KEYS); committed
      settings.local.md         per-user overrides; gitignored
      ON_PROMPT.md ...          project rules added to a command, one file per command
      ON_PROMPT.local.md ...    one user's rules for that command; gitignored
    <project>-project/          the project folder: project knowledge
      wip/wip.md                optional list of the work in progress
      <project>-usage/          optional usage folder: usage knowledge. The
                                `usage_folders` setting can keep it elsewhere,
                                and can name more than one
    <anything-else>/            background folders, real or symlinked: read-only

A project keeps two kinds of knowledge apart, because they have two readers.
Project knowledge is what an agent needs to work on the project, and it lives
in the project folder. Usage knowledge is what an agent in another project
needs to use it, and it lives in the usage folders. The commands write to those
folders and to nothing else in the knowledge base.

Knowledge comes from three places. The project folder and the usage folders
are this repository's own. Background folders are mounted beside the project
folder. Global folders stay where they are, outside context-db/: the
`global_context` setting holds glob patterns that find them, and `prompt` lists
what the patterns match. Another project's usage folder is the usual thing to
mount or to match.

Each of those folders is an Open Knowledge Format (OKF) bundle.

Settings are layered. A settings file can name more settings files on a
`settings_files` line; they are read after it and override it (settings_order).

Requires Python 3.8+ and nothing outside the standard library.
"""

import argparse
import datetime
import glob
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
LOCAL_GLOB = "*.local.md"  # every per-user file in configuration/; gitignored
REQUIRED_SETTINGS = ("project", "python", "main_branch")
# usage_folders: where the usage folders are kept, as paths read from the
# repository root; {project} in one stands for the project name. Left out,
# there is one: <project>-usage inside the project folder.
# global_context: glob patterns, read from the repository root, that match
# knowledge folders outside context-db/. `prompt` lists them.
OPTIONAL_SETTINGS = ("usage_folders", "global_context")
SETTINGS_KEYS = REQUIRED_SETTINGS + OPTIONAL_SETTINGS
# The setting with which a settings file names more settings files, as paths
# read from the repository root. Each is read after the file that names it and
# overrides it. It is written by hand: no command sets it.
SETTINGS_FILES = "settings_files"
# These three hold a list: one value on the key's line, or a YAML list. Several
# values on one line are refused, so a value cannot contain a space.
LIST_SETTINGS = OPTIONAL_SETTINGS + (SETTINGS_FILES,)
LIST_SEPARATOR = "\n"  # a list is kept as one string, its items joined by this
PROJECT_NAME = "{project}"  # stands for the project name in the usage_folders setting
WIP_LIST_NAME = "wip.md"
INDEX_NAME = "index.md"
RESERVED_FILES = (INDEX_NAME, "log.md")
STATUSES = ("draft", "stable", "deprecated")
ON_COMMANDS = ("prompt", "update", "wip", "maintain", "configure")
AGENT_NOTE_FILES = ("AGENTS.md", "CLAUDE.md")
# The three sizes behind progressive disclosure: what an agent reads before it
# opens a file, what it loads when it does, and what it scans at each level.
MAX_DESCRIPTION_CHARS = 300
MAX_FILE_LINES = 200
MAX_FOLDER_ITEMS = 12
MAX_INDEX_TITLES = 8  # how many entries of an index.md stand in for a missing description
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
Before a question or task. Navigates the Open Knowledge Format files of the
knowledge base, based on what you ask.
""",
    "update": """
After a task. Writes down what this session learned, if the next agent would
need it.
""",
    "wip": """
Optional, for long work. Keeps a short list of the work in progress. --list,
--maintain, --clear.
""",
    "maintain": """
Rarely, as a spring cleaning. Goes through the whole knowledge base against
the code and the git history: removes what the project already says and what
is no longer needed, fixes what has drifted, and splits and reorganizes.
""",
    "configure": """
First, and whenever you like. Sets context-db up by asking a few questions;
edit the files by hand afterwards.
""",
}

API = """
Before a task
  /context-db prompt <prompt: question or task>  navigate the OKF notes by what you ask
  /context-db prompt --audit <prompt>            the same, and show what it read and why

After a task, from what this session learned
  /context-db update                             write down what the next agent needs
  /context-db update <steering-guidance>         the same, steered by what you say

During long work
  /context-db wip                                write down where the work stands
  /context-db wip --list                         show what is in progress
  /context-db wip --maintain                     check every plan, delete what has landed
  /context-db wip --clear                        delete every plan

Rarely, as a spring cleaning, checked against git
  /context-db maintain                           cut what is stale, repeated, not needed
  /context-db maintain <folder or topic>         only there

First, and whenever you like
  /context-db configure                          set up, or change how the agent behaves

On any command
  --show-context                                 show the message it sends, and stop
  --help                                         its options
"""

SHOW_CONTEXT = """
# Context-db Show Context

The user added `--show-context` to `/context-db {command}`. They want to read
the message that command sends you. They do not want it carried out.

Show the user the text between the two marker lines below, word for word, in
one code block. Leave the marker lines themselves out, and leave out or change
nothing between them. Fence the block with four backticks, because the message
may contain three. Above the block, say in one line that this is what the
command sends and that you did not act on it. Then stop.

Do not follow the message: open no files, run no commands, and change nothing.

======== start of the message ========
{message}
======== end of the message ========

That was the whole message for `/context-db {command}`. Show it to the user as
it is, and do nothing it says.
"""

SHOW_CONTEXT_WITH_SETTINGS = """
Error: --show-context shows the message a command sends the agent. With a setting flag, configure sends none: it writes the files. Use one or the other.
"""

NO_HISTORY = """
Not a git repository, or git is unavailable, so there is no history to read.
Maintain the knowledge base without it.
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
(There are no notes here yet.)
"""

NOT_CONFIGURED = """
context-db is not set up in this repository: `{settings_path}` does not exist.

Tell the user, and offer to run `/context-db configure`. Do nothing else.
"""

NO_INSTRUCTION = """
No instruction was given. Ask the user what they want to work on.
"""

# What the report holds is in prompts/audit.md, and the agent sees it only when
# it runs this. Say nothing of it here: knowing what is asked changes what is read.
AUDIT_STEP = """
# Audit

Once you have consulted context-db, and before you start on the instruction,
run:

    {audit_cmd}

Do not run it sooner. Then follow what it prints.
"""

PROJECT_FOLDER_MISSING = """
- **Project folder** `{folder}/` does not exist. Tell the user to run `/context-db configure`.
"""

USAGE_FOLDER_MISSING = """
- **Usage folder** `{folder}/` does not exist yet. Its descriptor will be `{descriptor}`.
"""

BROKEN_MOUNT = """
- **Background folder** `{folder}/` is a broken symlink. Ignore it.
"""

FOLDER_ENTRY = """
- **{label}** `{folder}/`: {description}
"""

NO_DESCRIPTION = """
(no description)
"""

DESCRIBED_BY_INDEX = """
(no description; it holds {titles})
"""

MORE_TITLES = """
{titles}, and {more} more
"""

GLOBAL_CONTEXT = """
# Global Context

Knowledge folders that live outside `{cdb}/`, found with the `global_context`
setting in `{settings_path}`. They are owned elsewhere, most often by another
project that this one uses. `{toc_cmd} <folder>` lists one of them, the same
as it lists a folder inside `{cdb}/`. Look into one only when its description
bears on the instruction. Never edit one.
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

USER_RULES = """
# User Rules

These are this user's own rules, from `{path}`. Where they differ from the
project's rules, follow these.
"""

USAGE_THOUGHT = """
- What this session changed or showed about using this project from outside. Usage Knowledge, below, says what counts.
"""

USAGE_HOME = """
a usage folder ({usage_list}). Usage Knowledge, below, says what goes there.
"""

NO_USAGE_HOME = """
a usage folder, which this project does not have yet. Start one only when the user asks for it: create its descriptor, `{descriptor}`, with a `description` that says what this project is and what the notes cover, then run `{update_cmd}` with the same instruction. It then says what belongs there.
"""

NOTHING_TO_ADD = """
tell the user there is nothing to change and stop
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

Read from its files just now. To look inside a subfolder, run `{toc_cmd} <path>`, with the path exactly as it appears in the subfolder's link below.
"""

TOC_KEEPS_INDEX = """
This folder also keeps an index file, `{index}`, for people and for other tools. If you add, rename, or delete a file or a subfolder here, change its line in that file to match.
"""

TOC_FROM_INDEX = """
# Contents of `{folder}/`

Read from `{index}`, the index file this folder came with from its owner, with its links rewritten to start from the current directory. To look inside a subfolder, run `{toc_cmd} <path>`, with the path exactly as it appears in the subfolder's link below.
"""

TOC_EMPTY = """
Nothing is in this folder yet.
"""

INDEX_OMITS = """
{path}: does not list {names} — add a line for each, in the form `* [Title](name) - description`
"""

INDEX_LISTS_MISSING = """
{path}: lists `{target}`, which is not there — remove the line
"""

LONG_DESCRIPTION = """
{path}: description is {length} characters — say what the file holds in a line or two; if that takes more, the file holds several topics and should be split (max {limit})
"""

LONG_FOLDER_DESCRIPTION = """
{path}: description is {length} characters — say what kind of thing the folder holds in a line or two, and leave the list of its files to `toc` (max {limit})
"""

LINK_LEAVES_USAGE = """
{path}: link `{target}` leaves the usage folder — other projects read that folder from wherever they mount it, so link only to files inside it
"""

UNKNOWN_SETTING = """
Error: {path} has a setting that context-db does not know: {keys}. The settings are {known}. Fix the spelling, or delete the line.
"""

SEVERAL_VALUES_ON_A_LINE = """
Error: `{key}` in {path} holds several values on one line. Write them as a list, one to a line:

{key}:
{items}
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
- main_branch: the branch that `/context-db wip --maintain` checks the plans
  against.

Three more are optional. Add them as lines of their own:

- usage_folders: where the usage folders are kept, as paths from the top of
  the repository, such as okf/{{project}}-usage. {{project}} stands for the
  project name. Left out, there is one: <project>-usage/ inside the project
  folder. A usage folder holds what other projects need to know to use this
  one, and `/context-db update` writes it.
- global_context: glob patterns that match knowledge folders outside
  context-db/, such as ../*/okf/*-usage. They are read from the top of the
  repository. `/context-db prompt` lists the folders they match.
- settings_files: more settings files to read, such as
  ~/.config/context-db/team.md. Each is read after this file and overrides
  it.

Each of the three takes one value on its line, or several as a list:

    global_context:
      - okf/*-usage
      - ../*/okf/*-usage

settings.local.md in this folder, if it exists, is read after those and
overrides any of this for one user. Every *.local.md file in this folder is
gitignored.
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
    """The command printed for the agent to run next.

    Started as an installed `context-db` command, that command, as it was invoked: a path
    such as ``../bin/context-db`` keeps the agent on the same installation, instead of
    whichever ``context-db`` comes first on PATH. Otherwise, the script, run with `python`.
    """
    invoked = sys.argv[0]
    if os.path.basename(invoked) == "context-db":
        return shlex.quote(rel(invoked) if os.path.isabs(invoked) else invoked)
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
#
# A settings file can name more settings files on its `settings_files` line: one
# that a team shares between projects, or one that a user keeps for all of
# theirs. They are read right after the file that names them, so the order is
# settings.md, the files it names, settings.local.md, the files it names. A
# later file overrides an earlier one, key by key. The named files are only
# ever read; the user writes them.


def conf_dir(cdb):
    return os.path.join(cdb, CONF_DIR_NAME)


def settings_path(cdb, local=False):
    return os.path.join(conf_dir(cdb), LOCAL_SETTINGS_NAME if local else SETTINGS_NAME)


def from_root(cdb, path):
    """Where a path or a pattern in the settings points: it is read from the repository root.

    `~` and absolute paths work too.
    """
    return os.path.join(os.path.dirname(os.path.abspath(cdb)), os.path.expanduser(path))


def load_settings(path):
    """Return (values, problem). The problem is None when the file is usable."""
    if not os.path.isfile(path):
        return None, "does not exist"
    meta, _ = parse_frontmatter(read_text(path), LIST_SETTINGS)
    if meta is None:
        return None, "has no `---` block at the top holding the settings"
    return meta, None


def read_settings(path, named_by=""):
    """The values in a settings file. Stops when it is unusable, saying which file names it."""
    values, problem = load_settings(path)
    if problem and named_by:
        sys.exit(
            f"Error: {path} {problem}. The `settings_files` line in {named_by} names it. "
            "Fix the file, or take it off that line."
        )
    if problem:
        sys.exit(f"Error: {path} {problem}. Fix it by hand, or delete it and run configure.")
    return values


def list_items(value):
    """The items of a setting that holds a list, as parse_frontmatter returns it."""
    return [item for item in value.split(LIST_SEPARATOR) if item]


def named_settings(cdb, value):
    """The files that a `settings_files` value names, as paths from the cwd."""
    return [rel(from_root(cdb, name)) for name in list_items(value)]


def settings_order(cdb):
    """Every settings file in the order it is read, as (path, the file that names it).

    settings.md and settings.local.md are named by nothing and are listed even
    when they do not exist. A file is read once, where it is first named, so
    files that name each other cannot loop.
    """
    order = []

    def add(path, named_by):
        if any(path == listed for listed, _ in order):
            return
        order.append((path, named_by))
        values = load_settings(path)[0] or {}
        for named in named_settings(cdb, values.get(SETTINGS_FILES, "")):  # an optional line
            add(named, path)

    for local in (False, True):
        add(settings_path(cdb, local), "")
    return order


def setting_lines(key, value):
    """A setting as it is written: on one line, or as a YAML list when it holds several values."""
    if key not in LIST_SETTINGS:
        return [f"{key}: {value}"]
    items = [f'"{item}"' if scalar_problem([item]) else item for item in list_items(value)]
    if len(items) == 1:
        return [f"{key}: {items[0]}"]
    return [f"{key}:"] + [f"  - {item}" for item in items]


def write_settings(path, values, default_body):
    """Rewrite the frontmatter of a settings file, keeping whatever body it has."""
    body = read_doc(path)[1] if os.path.isfile(path) else "\n" + text(default_body) + "\n"
    keys = [key for key in SETTINGS_KEYS if key in values]
    keys += [key for key in values if key not in SETTINGS_KEYS]
    header = "\n".join(line for key in keys for line in setting_lines(key, values[key]))
    write_text(path, f"---\n{header}\n---\n{body}")


def unknown_settings(values):
    """The keys of a settings file that are not settings.

    Settings files are written by hand, and a misspelt key would otherwise be
    ignored without a word.
    """
    return [key for key in values if key not in SETTINGS_KEYS + (SETTINGS_FILES,)]


def crowded_settings(values):
    """The list settings that hold several values on one line, which is not a list."""
    return [
        key
        for key in LIST_SETTINGS
        if any(
            len(item.split()) > 1 for item in list_items(values.get(key, ""))
        )  # optional settings
    ]


def check_settings(values, path):
    """Stop on a key that is not a setting, and on several values squeezed onto one line."""
    unknown = unknown_settings(values)
    if unknown:
        keys = ", ".join(f"`{key}`" for key in unknown)
        known = ", ".join(SETTINGS_KEYS + (SETTINGS_FILES,))
        sys.exit(text(UNKNOWN_SETTING, path=path, keys=keys, known=known))
    for key in crowded_settings(values):
        items = "\n".join(f"  - {item}" for item in values[key].split())
        sys.exit(text(SEVERAL_VALUES_ON_A_LINE, path=path, key=key, items=items))


def load_config(cdb):
    """The settings from every file in settings_order, or None when there is no settings.md."""
    shared_path = settings_path(cdb)
    if not os.path.isfile(shared_path):
        return None
    config = {}
    for path, named_by in settings_order(cdb):
        if not named_by and not os.path.isfile(path):
            continue  # settings.local.md is optional; a file that is named is not
        values = read_settings(path, named_by)
        check_settings(values, path)
        config.update(values)
    missing = [key for key in REQUIRED_SETTINGS if not config.get(key)]  # frontmatter: all optional
    if missing:
        sys.exit(f"Error: {shared_path} has no {', '.join(missing)}. Run /context-db configure.")
    return config


def require_config(cdb, args):
    config = load_config(cdb)
    if config is None:
        emit(args, [text(NOT_CONFIGURED, settings_path=settings_path(cdb))])
        sys.exit(0)
    return config


def configured(cdb, key, default=""):
    """One setting if the settings can be read, else the default. Never fails.

    For `configure`, which must work on missing or broken settings, and for
    `toc`, which works on any folder.
    """
    value = default
    for path, _ in settings_order(cdb):
        values = load_settings(path)[0]
        if values and values.get(key):  # frontmatter: any file may leave it out
            value = values[key]
    return value


def project_dir(cdb, config):
    return os.path.join(cdb, f"{config['project']}-project")


def usage_dirs(cdb, config):
    """The usage folders: what agents in other projects need to know to use this one.

    The `usage_folders` setting names them. Left out, there is one:
    <project>-usage inside the project folder. A folder is listed whether or
    not it exists yet.
    """
    name = config["project"]
    named = list_items(config.get("usage_folders", ""))  # an optional setting
    if not named:
        return [os.path.join(project_dir(cdb, config), f"{name}-usage")]
    folders = [rel(from_root(cdb, folder.replace(PROJECT_NAME, name))) for folder in named]
    return list(dict.fromkeys(folders))


def usage_root(folder, usage):
    """The one of the usage folders that a folder lies in, or "" when it is in none."""
    return next((root for root in usage if within(folder, root)), "")


def own_bundles(cdb, config):
    """The bundles the commands write: the project folder, and each usage folder kept outside it."""
    project = project_dir(cdb, config)
    usage = usage_dirs(cdb, config)
    outside = [folder for folder in usage if os.path.isdir(folder) and not within(folder, project)]
    return [project] + outside


def global_patterns(config):
    return list_items(config.get("global_context", ""))  # an optional setting


# ── Frontmatter ──────────────────────────────────────────────────────────────
# Hand-rolled, because the skill must run on a bare interpreter with no PyYAML.
# It reads top-level scalar keys only, in every scalar style an LLM produces:
# inline, quoted, folded onto continuation lines, or behind a block indicator.
# The settings that hold a list are the one exception: for the keys a caller
# names, it also reads a YAML list, written under the key or in brackets.
#
# Every key is optional as far as the parser is concerned, so callers read the
# result with .get(). Whether a key is required is lint's decision, not this
# parser's.

KEY_RE = re.compile(r"^([A-Za-z_][\w-]*):(?:\s+(.*))?$")
BLOCK_SCALAR_RE = re.compile(r"^[>|][-+0-9]*$")
LIST_ITEM_RE = re.compile(r"^\s*-\s+(.+?)\s*$")
FLOW_LIST_RE = re.compile(r"^\[(.*)\]$")


def unquoted(value):
    """A YAML scalar without its quotes."""
    if len(value) >= 2 and value[0] == value[-1] == '"':
        return value[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    if len(value) >= 2 and value[0] == value[-1] == "'":
        return value[1:-1].replace("''", "'")
    return value


def parse_frontmatter(content, lists=()):
    """Return (meta, body). meta is None when there is no frontmatter block.

    `lists` names the keys that may hold a YAML list. Such a value comes back
    as its items joined by LIST_SEPARATOR; one value on the key's line is a
    list of one.
    """
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
    items = {}  # the keys written as a YAML list, with their items
    key = None
    for line in lines[1:end]:
        match = KEY_RE.match(line)
        item = LIST_ITEM_RE.match(line)
        if match:
            key = match.group(1)
            value = (match.group(2) or "").strip()
            meta[key] = "" if BLOCK_SCALAR_RE.match(value) else value
            flow = FLOW_LIST_RE.match(value) if key in lists else None
            if flow:
                items[key] = [part.strip() for part in flow.group(1).split(",") if part.strip()]
            elif key in lists and not value:
                items[key] = []
        elif key in items and item and not meta[key]:
            items[key].append(item.group(1))
        elif key and line[:1] in (" ", "\t") and line.strip():
            meta[key] = (meta[key] + " " + line.strip()).strip()
    for key, value in meta.items():
        meta[key] = unquoted(value)
    for key, found in items.items():
        if found:
            meta[key] = LIST_SEPARATOR.join(unquoted(part) for part in found)
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


def knowledge_folders(cdb):
    """The folders at the top of context-db/ that hold notes.

    A background folder is mounted there as a symlink, so a link counts here,
    as it does nowhere else. The settings folder holds no notes.
    """
    return sorted(
        name
        for name in os.listdir(cdb)
        if visible(name)
        and name != CONF_DIR_NAME
        and os.path.isdir(os.path.join(cdb, name))
        and has_knowledge(os.path.join(cdb, name))
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


def within(path, parent):
    """True when path is parent or lies under it, with symlinks resolved."""
    path, parent = os.path.realpath(path), os.path.realpath(parent)
    return os.path.commonpath([parent, path]) == parent


# A folder that context-db does not own may come with the index.md that OKF
# allows: one line per child, written by whoever owns the folder. Where there is
# one it is used as it stands. The project folder never has one.

LINK_RE = re.compile(r"\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
INDEX_ENTRY_RE = re.compile(r"(?m)^\s*[*+-]\s+\[([^\]]+)\]\(")


def index_path(folder):
    path = os.path.join(folder, INDEX_NAME)
    return path if os.path.isfile(path) else None


def index_body(folder):
    """What the folder's own index.md says below its frontmatter. "" when it has none."""
    path = index_path(folder)
    return read_doc(path)[1].strip() if path else ""


def index_listing(folder):
    """The folder's own index.md, with its links rewritten to start from the caller's cwd."""

    def from_cwd(match):
        link, target = match.group(0), match.group(1)
        if SCHEME_RE.match(target) or target.startswith(("#", "/")):
            return link
        path, mark, anchor = target.partition("#")
        moved = os.path.normpath(os.path.join(folder, path)) + ("/" if path.endswith("/") else "")
        start = match.start(1) - match.start(0)
        return link[:start] + moved + mark + anchor + link[start + len(target) :]

    return LINK_RE.sub(from_cwd, index_body(folder))


def folder_description(folder):
    """The description in the folder's descriptor. Without one, what its own index.md lists."""
    path = descriptor_path(folder)
    description = (read_doc(path)[0] or {}).get("description", "") if path else ""
    titles = [] if description else INDEX_ENTRY_RE.findall(index_body(folder))
    if not titles:
        return description
    listed = ", ".join(titles[:MAX_INDEX_TITLES])
    if len(titles) > MAX_INDEX_TITLES:
        listed = text(MORE_TITLES, titles=listed, more=len(titles) - MAX_INDEX_TITLES)
    return text(DESCRIBED_BY_INDEX, titles=listed)


# ── Folder listings ──────────────────────────────────────────────────────────
# OKF's index.md is a progressive-disclosure file: one line per child, each with
# its description. context-db never writes one. `toc` prints the same listing
# from the frontmatter as it is at that moment, so there is nothing to keep in
# step and nothing to commit.


def toc_entry(title, target, description):
    title = title.replace("[", "\\[").replace("]", "\\]")
    line = f"* [{title}]({target})"
    return f"{line} - {description}" if description else line


def folder_listing(folder, toc_cmd, use_index, subfolders=None):
    """The OKF index of a folder. Paths are relative to the caller's cwd.

    `subfolders` names the subfolders to list, for the one folder whose own
    are not found the usual way: the top of context-db/.

    It is built now, from the folder's files. With use_index, a folder that
    comes with an index.md of its own that lists something is shown from that.
    Without it, a folder that keeps an index.md says so, because whoever
    changes the folder has to change that file too.
    """
    listing = index_listing(folder) if use_index else ""
    if listing:
        heading = text(TOC_FROM_INDEX, folder=folder, index=index_path(folder), toc_cmd=toc_cmd)
        return f"{heading}\n\n{listing}"

    descriptor = descriptor_path(folder)
    sub_lines = []
    for name in folder_subfolders(folder) if subfolders is None else subfolders:
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
    if not use_index and index_path(folder):
        parts.append(text(TOC_KEEPS_INDEX, index=index_path(folder)))
    if sub_lines:
        parts.append("# Subfolders\n\n" + "\n".join(sub_lines))
    if file_lines:
        parts.append("# Files\n\n" + "\n".join(file_lines))
    if not sub_lines and not file_lines:
        parts.append(text(TOC_EMPTY))
    return "\n\n".join(parts)


# ── Lint ─────────────────────────────────────────────────────────────────────


def lint_links(path, body, usage):
    """Problems with a file's links. In a usage folder, a link may not leave it."""
    problems = []
    for target in LINK_RE.findall(strip_code(without_comments(body))):
        if SCHEME_RE.match(target) or target.startswith("#"):
            continue
        target = unquote(target.split("#")[0])
        linked = os.path.join(os.path.dirname(path), target)
        if target.startswith("/"):
            problems.append(f"{path}: link `{target}` starts with / — make it relative to the file")
        elif not os.path.exists(linked):
            problems.append(f"{path}: broken link `{target}`")
        elif usage and not within(linked, usage):
            problems.append(text(LINK_LEAVES_USAGE, path=path, target=target))
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


def index_drift(folder):
    """Where a folder's index.md and the folder disagree, as warnings.

    For a folder the commands write. `toc` lists such a folder from its files,
    so an index.md there is the project's own choice, kept for people and for
    other OKF tools, and worth having only while it is in step.
    """
    path = index_path(folder)
    if not path:
        return []
    listed = []
    for target in LINK_RE.findall(strip_code(without_comments(read_doc(path)[1]))):
        if not SCHEME_RE.match(target) and not target.startswith(("#", "/")):
            listed.append(os.path.normpath(os.path.join(folder, unquote(target.split("#")[0]))))
    warnings = [
        text(INDEX_LISTS_MISSING, path=path, target=target)
        for target in listed
        if not os.path.exists(target)
    ]
    descriptor = descriptor_path(folder)
    omitted = [
        name
        for name in folder_files(folder)
        if os.path.join(folder, name) not in listed
        and not (descriptor and os.path.samefile(os.path.join(folder, name), descriptor))
    ]
    for name in folder_subfolders(folder):
        inside = os.path.join(folder, name) + os.sep
        if not any((target + os.sep).startswith(inside) for target in listed):
            omitted.append(f"{name}/")
    if omitted:
        names = ", ".join(f"`{name}`" for name in omitted)
        warnings.append(text(INDEX_OMITS, path=path, names=names))
    return warnings


def lint_file(path, in_wip, usage):
    """Return (errors, warnings) for one file. `usage` is the usage folder the file is in, or ""."""
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
    errors.extend(lint_links(path, body, usage))
    length = len(meta.get("description", ""))
    if length > MAX_DESCRIPTION_CHARS:
        too_long = LONG_FOLDER_DESCRIPTION if meta.get("type") == "Folder" else LONG_DESCRIPTION
        warnings.append(text(too_long, path=path, length=length, limit=MAX_DESCRIPTION_CHARS))
    lines = content.count("\n")
    if lines > MAX_FILE_LINES and not in_wip:
        warnings.append(f"{path}: {lines} lines — split into a subfolder (max {MAX_FILE_LINES})")
    return errors, warnings


def lint_bundle(bundle, own, usage):
    """Return (errors, warnings) for one bundle.

    In a bundle the commands write (`own`), every folder needs a descriptor, and
    an index.md is checked against what its folder holds. In any other bundle a
    folder's index.md stands in for a descriptor. `usage` is the list of usage
    folders: a file in one of them links only inside it.
    """
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

    wip = os.path.join(bundle, "wip")
    if is_real_dir(wip):
        warnings.extend(unlisted_wip(wip))
    for folder in bundle_folders(bundle):
        files = folder_files(folder)
        if not descriptor_path(folder) and (own or not index_path(folder)):
            name = os.path.basename(os.path.realpath(folder))
            errors.append(f"{folder}/: no folder descriptor — add {name}.md with a description")
        items = len(files) + len(folder_subfolders(folder))
        if items > MAX_FOLDER_ITEMS:
            warnings.append(f"{folder}/: {items} items — split into subfolders (aim for 5–10)")
        if own:
            warnings.extend(index_drift(folder))
        in_wip = os.path.commonpath([wip, folder]) == wip
        in_usage = usage_root(folder, usage)
        for name in files:
            file_errors, file_warnings = lint_file(os.path.join(folder, name), in_wip, in_usage)
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


def on_file_path(cdb, command, local=False):
    """ON_<COMMAND>.md holds the project's rules; ON_<COMMAND>.local.md one user's."""
    suffix = ".local.md" if local else ".md"
    return os.path.join(conf_dir(cdb), f"ON_{command.upper()}{suffix}")


def on_file_rules(path):
    """The body of an ON file with frontmatter and HTML comments removed."""
    if not os.path.isfile(path):
        return ""
    return without_comments(read_doc(path)[1])


def on_file_text(cdb, command):
    """The project's rules for a command, then this user's own, each under a heading.

    A file that starts with a heading of its own keeps it.
    """
    project = on_file_rules(on_file_path(cdb, command))
    if project and not project.startswith("#"):
        project = f"# Project Rules\n\n{project}"
    local_path = on_file_path(cdb, command, local=True)
    user = on_file_rules(local_path)
    if user and not user.startswith("#"):
        user = f"{text(USER_RULES, path=local_path)}\n\n{user}"
    return "\n\n".join(part for part in (project, user) if part)


def emit(args, sections):
    """Print a command's message.

    With --show-context the same message is wrapped in an instruction to show it
    to the user and not to act on it.
    """
    message = "\n\n".join(section for section in sections if section)
    if args.show_context:
        message = text(SHOW_CONTEXT, command=args.command, message=message)
    print(message)


def instruction_of(args):
    """The user's instruction. A lone `-` means: read it from standard input."""
    if args.instruction == ["-"]:
        return sys.stdin.read().strip()
    return " ".join(args.instruction).strip()


def instruction_section(instruction):
    if not instruction:
        return ""
    return f"# User Instruction\n\n{instruction}"


def folder_entry(label, folder):
    description = folder_description(folder) or text(NO_DESCRIPTION)
    return text(FOLDER_ENTRY, label=label, folder=folder, description=description)


def folders_section(cdb, config, usage_missing=False):
    """The project folder first, then the usage folders, then every background folder.

    This list is generated on every call rather than committed, because a user
    may mount private folders through gitignored symlinks. A usage folder that
    does not exist yet is left out, unless usage_missing asks for a line that
    says so.
    """
    project, usage = project_dir(cdb, config), usage_dirs(cdb, config)
    lines = ["# Folders", ""]
    if os.path.isdir(project):
        lines.append(folder_entry("Project folder", project))
    else:
        lines.append(text(PROJECT_FOLDER_MISSING, folder=project))
    for folder in usage:
        if os.path.isdir(folder):
            lines.append(folder_entry("Usage folder", folder))
        elif usage_missing:
            descriptor = os.path.join(folder, f"{os.path.basename(folder)}.md")
            lines.append(text(USAGE_FOLDER_MISSING, folder=folder, descriptor=descriptor))

    for name in sorted(os.listdir(cdb)):
        folder = os.path.join(cdb, name)
        if not visible(name) or name == CONF_DIR_NAME or folder in [project] + usage:
            continue
        if os.path.islink(folder) and not os.path.exists(folder):
            lines.append(text(BROKEN_MOUNT, folder=folder))
        elif os.path.isdir(folder):
            lines.append(folder_entry("Background folder", folder))
    return "\n".join(lines)


def global_folders(cdb, config):
    """The folders that the `global_context` patterns match, in the order found.

    Each pattern is a glob read from the repository root, wherever the command
    was run from; `~` and absolute paths work too. A folder that context-db/
    already holds, itself or through a symlink, is left out, so a pattern such
    as ../*/context-db/*-project does not list this project twice. So are this
    project's own usage folders, which a pattern for usage folders also matches.
    """
    seen = {os.path.realpath(os.path.join(cdb, name)) for name in os.listdir(cdb)}
    if config.get("project"):  # configure reports the matches even before a project is set
        seen.update(os.path.realpath(folder) for folder in usage_dirs(cdb, config))
    found = []
    for pattern in global_patterns(config):
        for match in sorted(glob.glob(from_root(cdb, pattern), recursive=True)):
            real = os.path.realpath(match)
            if os.path.isdir(match) and real not in seen and not within(real, cdb):
                seen.add(real)
                found.append(rel(match))
    return found


def global_context_section(cdb, config):
    """One line for each global folder, or "" when the patterns match none."""
    folders = global_folders(cdb, config)
    if not folders:
        return ""
    toc_cmd = f"{script_command(config['python'])} toc"
    intro = text(GLOBAL_CONTEXT, toc_cmd=toc_cmd, cdb=cdb, settings_path=settings_path(cdb))
    entries = "\n".join(folder_entry("Global folder", folder) for folder in folders)
    return f"{intro}\n\n{entries}"


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


def has_plans(cdb, config):
    """Whether wip/ lists or holds any plan."""
    if wip_list(cdb, config):
        return True
    wip = wip_dir(cdb, config)
    if not os.path.isdir(wip):
        return False
    return bool(folder_subfolders(wip)) or folder_files(wip) not in ([], [WIP_LIST_NAME])


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


def plan_check_sections(cdb, config):
    """How the plans are checked, the git state to check them against, and the list."""
    return [
        load_prompt(
            "wip-check",
            wip_list=wip_list_path(cdb, config),
            wip_dir=wip_dir(cdb, config),
            project_dir=project_dir(cdb, config),
            main=config["main_branch"],
        ),
        git_state_section(cdb, config),
        wip_section(cdb, config, WIP_LISTED, show_empty=True),
    ]


# The history `maintain` reads: for each note, how far the project has moved
# since the note last changed.

MAX_HISTORY_NOTES = 60


def note_folders(cdb, config):
    """The folders that hold notes: context-db/ and the usage folders. The rest is the project."""
    return [cdb] + usage_dirs(cdb, config)


def outside_the_notes(cdb, config):
    """Git pathspecs for the whole repository except the folders that hold notes."""
    top = git("rev-parse", "--show-toplevel").strip()
    folders = [folder for folder in note_folders(cdb, config) if within(folder, top)]
    return [":/"] + [f":(exclude){folder}" for folder in folders]


def bundle_notes(bundle, leave_out):
    """Every note in a bundle, descriptors with a body included, outside the `leave_out` folders."""
    notes = []
    for folder in bundle_folders(bundle):
        if any(within(folder, left_out) for left_out in leave_out):
            continue
        descriptor = descriptor_path(folder)
        for name in folder_files(folder):
            path = os.path.join(folder, name)
            body = read_doc(path)[1]
            if descriptor and os.path.samefile(path, descriptor) and not body.strip():
                continue
            notes.append((path, body))
    return notes


def linked_project_files(path, body, notes):
    """The files a note links to that exist and lie outside `notes`, the folders that hold notes."""
    found = []
    tops = [os.path.abspath(folder) for folder in notes]
    for target in LINK_RE.findall(strip_code(without_comments(body))):
        if SCHEME_RE.match(target) or target.startswith(("#", "/")):
            continue
        linked = os.path.normpath(
            os.path.join(os.path.dirname(path), unquote(target.split("#")[0]))
        )
        is_note = any(os.path.commonpath([top, os.path.abspath(linked)]) == top for top in tops)
        if os.path.exists(linked) and not is_note:
            found.append(linked)
    return sorted(set(found))


def git_history_section(cdb, config):
    """Each note against the commits made to the rest of the project since it last changed.

    The notes are the project folder's and the usage folders'. The plans in wip/
    are left out: they are checked against the state of the branch instead.
    """
    if not current_branch():
        return "# Git History\n\n" + text(NO_HISTORY)
    notes = note_folders(cdb, config)
    outside = outside_the_notes(cdb, config)
    usage = usage_dirs(cdb, config)
    found = bundle_notes(project_dir(cdb, config), [wip_dir(cdb, config)] + usage)
    found += [
        note for folder in usage if os.path.isdir(folder) for note in bundle_notes(folder, [])
    ]
    rows = []  # (linked files changed, commits behind, line), most out of date sorts first
    for path, body in found:
        last = git("log", "-1", "--format=%h %as", "--", path).split()
        if not last:
            rows.append((False, -1, text(HISTORY_NOT_COMMITTED, path=path)))
            continue
        commit, date = last
        behind = int(git("rev-list", "--count", f"{commit}..HEAD", "--", *outside) or 0)
        line = text(HISTORY_ROW, path=path, date=date, commit=commit, behind=behind)
        linked = linked_project_files(path, body, notes)
        changed = (
            git("diff", "--name-only", f"{commit}..HEAD", "--", *linked).split() if linked else []
        )
        if changed:
            line += text(HISTORY_LINKED, files=", ".join(f"`{name}`" for name in changed))
        rows.append((bool(changed), behind, line))
    rows.sort(key=lambda row: (row[0], row[1]), reverse=True)
    lines = [load_prompt("maintain-git"), ""]
    lines.extend(line for _, _, line in rows[:MAX_HISTORY_NOTES])
    if len(rows) > MAX_HISTORY_NOTES:
        lines.append(f"- ... ({len(rows) - MAX_HISTORY_NOTES} more notes)")
    if not rows:
        lines.append(text(HISTORY_EMPTY))
    return "\n".join(lines)


# ── Commands ─────────────────────────────────────────────────────────────────


def cmd_prompt(args):
    cdb = context_db_dir()
    config = require_config(cdb, args)
    instruction = instruction_of(args)
    if not instruction:
        emit(args, [text(NO_INSTRUCTION)])
        return
    branch = current_branch()
    on_branch = f" (the current branch is `{branch}`)" if branch else ""
    emit(
        args,
        [
            load_prompt("prompt", cdb=cdb),
            navigate_section(config),
            load_prompt("not-a-mirror"),
            wip_section(cdb, config, WIP_FOR_PROMPT, show_empty=False, on_branch=on_branch),
            folders_section(cdb, config),
            global_context_section(cdb, config),
            text(AUDIT_STEP, audit_cmd=f"{script_command(config['python'])} audit")
            if args.audit
            else "",
            on_file_text(cdb, "prompt"),
            instruction_section(instruction),
        ],
    )


def cmd_audit(args):
    """The second half of `prompt --audit`: what to report, once the reading is done."""
    emit(args, [load_prompt("audit")])


def usage_list(cdb, config):
    """The usage folders as one phrase for a sentence: `a/`, `b/`."""
    return ", ".join(f"`{folder}/`" for folder in usage_dirs(cdb, config))


def has_usage(cdb, config):
    """Whether any usage folder exists yet."""
    return any(os.path.isdir(folder) for folder in usage_dirs(cdb, config))


def cmd_update(args):
    """Store what the session learned, in the project folder and the usage folders."""
    cdb = context_db_dir()
    config = require_config(cdb, args)
    commit = args.commit or args.push
    script = script_command(config["python"])
    usage = has_usage(cdb, config)
    first_usage = usage_dirs(cdb, config)[0]
    names = {
        "usage_list": usage_list(cdb, config),
        "descriptor": os.path.join(first_usage, f"{os.path.basename(first_usage)}.md"),
        "update_cmd": f"{script} update",
        "toc_cmd": f"{script} toc",
    }
    sections = [
        load_prompt(
            "update",
            project_dir=project_dir(cdb, config),
            usage_thought="\n" + text(USAGE_THOUGHT) if usage else "",
            usage_home=text(USAGE_HOME if usage else NO_USAGE_HOME, **names),
            conf_dir=conf_dir(cdb),
            wip_dir=wip_dir(cdb, config),
            toc_cmd=f"{script} toc",
            check_cmd=f"{script} toc --check",
            nothing_to_add=text(NOTHING_TO_ADD_BUT_COMMIT if commit else NOTHING_TO_ADD),
        ),
        load_prompt("update-usage", **names) if usage else "",
        load_prompt("not-a-mirror"),
        load_prompt("keep-small"),
        navigate_section(config),
        folders_section(cdb, config, usage_missing=usage),
        load_prompt("format"),
    ]
    if commit:
        push = text(THEN_PUSH if args.push else DO_NOT_PUSH)
        sections.append(load_prompt("commit", cdb=cdb, push=push))
    sections.append(on_file_text(cdb, "update"))
    sections.append(instruction_section(instruction_of(args)))
    emit(args, sections)


def cmd_maintain(args):
    """Tidy the whole knowledge base: the project folder, its plans, and the usage folders."""
    cdb = context_db_dir()
    config = require_config(cdb, args)
    toc_cmd = f"{script_command(config['python'])} toc"
    sections = [
        load_prompt(
            "maintain",
            cdb=cdb,
            project_dir=project_dir(cdb, config),
            wip_dir=wip_dir(cdb, config),
            toc_cmd=toc_cmd,
            check_cmd=f"{toc_cmd} --check",
        ),
        load_prompt("not-a-mirror"),
        load_prompt("keep-small"),
        navigate_section(config),
        git_history_section(cdb, config),
        folders_section(cdb, config),
    ]
    if has_plans(cdb, config):
        sections.extend(plan_check_sections(cdb, config))
    if has_usage(cdb, config):
        sections.append(load_prompt("maintain-usage", usage_list=usage_list(cdb, config)))
    sections.append(load_prompt("format"))
    sections.append(on_file_text(cdb, "maintain"))
    sections.append(instruction_section(instruction_of(args)))
    emit(args, sections)


def cmd_wip(args):
    """Record the current work, or with a flag: list it, check every plan, or clear it all."""
    cdb = context_db_dir()
    config = require_config(cdb, args)
    mode = "list" if args.list else "maintain" if args.maintain else "clear" if args.clear else ""
    toc_cmd = f"{script_command(config['python'])} toc"
    values = {
        "project_dir": project_dir(cdb, config),
        "wip_dir": wip_dir(cdb, config),
        "wip_list": wip_list_path(cdb, config),
        "branch": current_branch() or "<branch>",
        "today": datetime.date.today().isoformat(),
        "check_cmd": f"{toc_cmd} --check",
    }
    sections = [load_prompt(f"wip-{mode}" if mode else "wip", **values)]
    if mode == "maintain":
        sections.extend(plan_check_sections(cdb, config))
    else:
        sections.append(wip_section(cdb, config, WIP_LISTED, show_empty=True))
    if mode != "list":
        sections.append(load_prompt("wip-format", **values))
    if mode in ("", "maintain"):
        sections.append(load_prompt("not-a-mirror"))
        sections.append(load_prompt("keep-small"))
        sections.append(navigate_section(config))
        sections.append(load_prompt("format"))
    sections.append(on_file_text(cdb, "wip"))
    sections.append(instruction_section(instruction_of(args)))
    emit(args, sections)


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


def v0_leftovers(cdb):
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
    old_scripts = os.path.join(SKILL_DIR, "scripts")
    if os.path.isdir(old_scripts):
        found.append(rel(old_scripts) + "/")
    return found


def current_rules_section(cdb):
    """What each ON file tells the agent today, for configure to show the user."""
    lines = ["# Current Rules", ""]
    for command in ON_COMMANDS:
        path = on_file_path(cdb, command)
        if not os.path.isfile(path):
            lines.extend([f"## `{path}` (does not exist yet; setting up creates it)", ""])
        else:
            lines.extend([f"## `{path}`, added to every `/context-db {command}`", ""])
            lines.extend([on_file_rules(path) or "(empty: it adds nothing)", ""])
        local_path = on_file_path(cdb, command, local=True)
        if os.path.isfile(local_path):
            lines.extend([f"## `{local_path}`, this user's own, added after it", ""])
            lines.extend([on_file_rules(local_path) or "(empty: it adds nothing)", ""])
    return "\n".join(lines).rstrip()


def cmd_configure(args):
    if wants_setup(args):
        if args.show_context:
            sys.exit(text(SHOW_CONTEXT_WITH_SETTINGS))
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

    # Every settings file, in the order it is read.
    mains = {settings_path(cdb): "Shared settings", settings_path(cdb, True): "Your own settings"}
    for path, named_by in settings_order(cdb):
        label = f"{mains[path]} `{path}`" if not named_by else f"Settings file `{path}`"
        label += f", named by `{named_by}`" if named_by else ""
        values, problem = load_settings(path)
        if not os.path.isfile(path):
            lines.append(f"- {label}: does not exist")
        elif problem:
            lines.append(f"- {label}: {problem}. Rewrite it by hand first.")
        else:
            shown = (
                ", ".join(
                    f"`{key}: {' '.join(list_items(value))}`" for key, value in values.items()
                )
                or "empty"
            )
            unknown = ", ".join(f"`{key}`" for key in unknown_settings(values))
            shown += (
                f". Not a setting, so the other commands stop on it: {unknown}" if unknown else ""
            )
            crowded = ", ".join(f"`{key}`" for key in crowded_settings(values))
            shown += (
                f". Several values on one line, which must be a list, so the other commands "
                f"stop on it: {crowded}"
                if crowded
                else ""
            )
            lines.append(f"- {label}: {shown}")

    found = ", ".join(f"`{os.path.join(cdb, n)}/`" for n in project_folders(cdb)) or "none"
    lines.append(f"- Project folders found: {found}")
    known = {key: configured(cdb, key) for key in ("project", "usage_folders", "global_context")}
    if known["project"]:
        named = " ".join(list_items(known["usage_folders"]))
        where = f"from `usage_folders: {named}`" if named else "in the default place"
        states = ", ".join(
            f"`{folder}/` ({'exists' if os.path.isdir(folder) else 'does not exist yet'})"
            for folder in usage_dirs(cdb, known)
        )
        lines.append(f"- Usage folders, {where}: {states}")
    patterns = " ".join(list_items(known["global_context"]))
    if patterns:
        folders = global_folders(cdb, known)
        matched = ", ".join(f"`{folder}/`" for folder in folders) or "no folders"
        lines.append(f"- Global context: `global_context: {patterns}` matches {matched}")
    else:
        lines.append("- Global context: no `global_context` setting")
    for note in AGENT_NOTE_FILES:
        path = os.path.join(root, note)
        if not os.path.isfile(path):
            lines.append(f"- `{rel(path)}`: does not exist")
        else:
            says = "mentions" if CONTEXT_DB in read_text(path) else "does not mention"
            lines.append(f"- `{rel(path)}`: exists, {says} `{CONTEXT_DB}/`")
    leftovers = v0_leftovers(cdb)
    if leftovers:
        listed = ", ".join(f"`{path}`" for path in leftovers)
        lines.extend(["", text(V0_LAYOUT_FOUND, leftovers=listed, guide=MIGRATION_GUIDE)])

    python = configured(cdb, "python", suggested_python)
    emit(
        args,
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
        ],
    )


def write_if_missing(path, content, created):
    if os.path.exists(path):
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    write_text(path, content)
    created.append(path)


def ignore_local_files(root, cdb):
    """Make sure no per-user file can ever be committed. Returns the line added.

    One glob covers them all: settings.local.md and every ON_<COMMAND>.local.md.
    """
    if not git("rev-parse", "--show-toplevel"):
        return ""
    per_user = [settings_path(cdb, True)] + [on_file_path(cdb, c, True) for c in ON_COMMANDS]
    if len(git("check-ignore", *per_user).splitlines()) == len(per_user):
        return ""
    line = f"{CONTEXT_DB}/{CONF_DIR_NAME}/{LOCAL_GLOB}"
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
    return bool(
        args.project
        or args.python
        or args.main_branch
        or args.usage_folder
        or args.global_context
        or args.local
    )


def cmd_setup(args):
    """Write the settings and create whatever is missing. Never overwrites a file."""
    root = find_repo_root()
    cdb = context_db_dir()
    shared_path = settings_path(cdb)
    local_path = settings_path(cdb, local=True)

    config = read_settings(shared_path) if os.path.isfile(shared_path) else {}
    check_settings(config, shared_path)
    previous_project = config.get("project")  # frontmatter: absent on the first run
    for key, value in (
        ("project", args.project),
        ("python", args.python),
        ("main_branch", args.main_branch),
        ("usage_folders", LIST_SEPARATOR.join(args.usage_folder or [])),
        ("global_context", LIST_SEPARATOR.join(args.global_context or [])),
    ):
        if value:
            config[key] = value
    check_settings(config, shared_path)
    if not config.get("project"):
        sys.exit("Error: no project name. Pass --project <name>.")
    check_project_name(cdb, config["project"])
    config.setdefault("python", "python3")
    config.setdefault("main_branch", detect_main_branch()[0])

    local = None
    if args.local:
        local = read_settings(local_path) if os.path.isfile(local_path) else {}
        check_settings(local, local_path)
        given = {}
        for item in args.local:
            key, separator, value = item.partition("=")
            if not separator or not value or key not in SETTINGS_KEYS:
                sys.exit(
                    "Error: --local takes KEY=VALUE, where KEY is one of "
                    f"{', '.join(SETTINGS_KEYS)}."
                )
            given.setdefault(key, []).append(value)
        for key, values in given.items():  # a list setting takes the flag once for each value
            local[key] = LIST_SEPARATOR.join(values) if key in LIST_SETTINGS else values[-1]
        check_settings(local, local_path)

    os.makedirs(conf_dir(cdb), exist_ok=True)
    write_settings(shared_path, config, SETTINGS_BODY)
    print(f"Wrote {shared_path}")
    if local is not None:
        write_settings(local_path, local, LOCAL_SETTINGS_BODY)
        print(f"Wrote {local_path}")
    ignored = ignore_local_files(root, cdb)
    if ignored:
        print(f"Added {ignored} to .gitignore")

    # The starters may name the command that runs this script; fill it in once,
    # with the shared interpreter, because the ON files are committed.
    python = config["python"]
    # Everything else follows the settings as the commands will read them, with
    # your own file and any named settings files applied.
    config = load_config(cdb)
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
    sys.exit(run_check(own_bundles(cdb, config), rerun, own=True, usage=usage_dirs(cdb, config)))


# ── toc ──────────────────────────────────────────────────────────────────────


def run_check(bundles, rerun, own, usage):
    """Print the format report for each bundle and return the exit code.

    `rerun` is the command to print for checking again. `own` and `usage` are
    what lint_bundle takes.
    """
    failed = 0
    for bundle in bundles:
        errors, warnings = lint_bundle(bundle, own, usage)
        for label, problems in (("ERROR", errors), ("WARNING", warnings)):
            for problem in problems:
                print(f"{label}: {problem}")
        failed += len(errors)
        if not errors:
            print(f"{bundle}/ is a conformant OKF v{OKF_VERSION} bundle.")
    if failed:
        print(f"\n{failed} error(s). Fix them, then run:  {rerun}")
        return 1
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


def cmd_toc(args):
    cdb = context_db_dir()
    toc_cmd = f"{script_command(configured(cdb, 'python', 'python3'))} toc"
    if args.folder:
        folder = os.path.normpath(args.folder)
        if not os.path.isdir(folder):
            sys.exit(
                f"Error: {folder}/ is not a folder. Pass the path exactly as listed in a "
                "table of contents; it is relative to the current directory, not to the "
                "folder that was listed."
            )
        bundles = [bundle_root(folder)]
    else:
        config = require_config(cdb, args)
        folder = project_dir(cdb, config)
        if not os.path.isdir(folder):
            sys.exit(f"Error: {folder}/ does not exist. Run /context-db configure.")
        bundles = own_bundles(cdb, config)  # with no folder given, --check covers them all

    # The project folder and the usage folders are context-db's own: the commands
    # write them, and every file in them has a description, so they are always
    # listed from the files, which cannot be out of date. An index.md kept there
    # is accepted and left unread. Everywhere else an index.md that came with a
    # folder is used. With no settings, no folder is context-db's own.
    known = {key: configured(cdb, key) for key in ("project", "usage_folders")}
    usage = usage_dirs(cdb, known) if known["project"] else []
    own = [project_dir(cdb, known)] + usage if known["project"] else []

    def is_own(path):
        return any(within(path, folder) for folder in own)

    if not args.check:
        top = os.path.isdir(cdb) and os.path.samefile(folder, cdb)
        mounted = knowledge_folders(folder) if top else None
        print(folder_listing(folder, toc_cmd, use_index=not is_own(folder), subfolders=mounted))
        return
    if bundles[0] != folder:
        print(f"{folder}/ is inside {bundles[0]}/; checking all of {bundles[0]}/.")
    rerun = f"{toc_cmd} --check" + (f" {shlex.quote(bundles[0])}" if args.folder else "")
    sys.exit(run_check(bundles, rerun, own=is_own(bundles[0]), usage=usage))


# ── CLI ──────────────────────────────────────────────────────────────────────


def build_parser():
    parser = argparse.ArgumentParser(
        prog="context-db",
        description="A Markdown knowledge base for coding agents, in Open Knowledge Format.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.epilog = API.strip("\n")
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
        sub.add_argument(
            "--show-context",
            action="store_true",
            help="Have the agent show you the message this command sends it, and do nothing else",
        )
        return sub

    p = command("prompt")
    p.add_argument(
        "--audit",
        action="store_true",
        help="Have the agent report what it read from the knowledge base and what led it "
        "there: once before it starts on the task, and again when it has finished",
    )

    p = command("update")
    p.add_argument(
        "--commit",
        action="store_true",
        help="Optional: then commit everything the session changed, and do not push",
    )
    p.add_argument("--push", action="store_true", help="Optional: then commit and push")

    p = command("wip")
    modes = p.add_mutually_exclusive_group()
    modes.add_argument(
        "--list", action="store_true", help="Show what is in progress; change nothing"
    )
    modes.add_argument(
        "--maintain",
        action="store_true",
        help="Check every plan against git and delete those whose work has landed",
    )
    modes.add_argument("--clear", action="store_true", help="Delete every plan, after asking")

    command("maintain")

    p = command("configure")
    setting = p.add_argument_group(
        "settings", "Pass any of these to write the files directly, with no questions asked"
    )
    setting.add_argument("--project", help="Project name; its folder is context-db/<name>-project/")
    setting.add_argument("--python", help="Command that runs this script (Python 3.8 or newer)")
    setting.add_argument("--main-branch", help="Branch that the plans are checked against")
    setting.add_argument(
        "--usage-folder",
        action="append",
        metavar="PATH",
        help="Where a usage folder is kept, from the repository root; {project} stands for "
        "the project name (repeatable). Without it: <name>-usage inside the project folder",
    )
    setting.add_argument(
        "--global-context",
        action="append",
        metavar="GLOB",
        help="Pattern, read from the repository root, that matches knowledge folders "
        "outside context-db/; quote it (repeatable)",
    )
    setting.add_argument(
        "--local",
        action="append",
        metavar="KEY=VALUE",
        help=f"Per-user override, written to {LOCAL_SETTINGS_NAME} (repeatable)",
    )

    # Left out of --help on purpose (no help= keyword): the agent runs it, and CI.
    p = subs.add_parser(
        "toc",
        description="List a folder's files and subfolders with their descriptions, "
        "read from the files now. With --check, check the format instead.",
    )
    p.add_argument("folder", nargs="?", default="", help="Default: the project folder")
    p.add_argument("--check", action="store_true", help="Check the format; exit 1 on any error")
    p.set_defaults(show_context=False)  # toc prints for the agent to use, never to show

    # Left out of --help as well: `prompt --audit` tells the agent when to run it.
    p = subs.add_parser(
        "audit", description="Print what `prompt --audit` has the agent report, after it has read."
    )
    p.set_defaults(show_context=False)
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
        "maintain": cmd_maintain,
        "configure": cmd_configure,
        "toc": cmd_toc,
        "audit": cmd_audit,
    }
    if args.command not in handlers:
        parser.print_help()
        return
    handlers[args.command](args)


if __name__ == "__main__":
    main()
