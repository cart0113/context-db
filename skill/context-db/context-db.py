#!/usr/bin/env python3
"""
context-db.py — the one script behind the /context-db skill.

User-facing commands print instructions that the calling agent follows:

  prompt "<task>"         Consult the knowledge base for a piece of work.
  update ["<learning>"]   File a learning (--commit / --push to commit the session).
  wip ["<instruction>"]   Set up, refresh, and clean the current work in progress.
  configure               Create or repair the config and scaffold missing pieces.

Helper commands do deterministic file work on the agent's behalf:

  init                    Write the config and scaffold whatever is missing.
  index [bundle]          Regenerate index.md files and lint a bundle (--check to verify).

Layout this script assumes (see prompts/format.md for the file format):

  context-db/
    context-db.json             committed config
    context-db.local.json       optional per-user overrides, gitignored
    context-db-on-markdown/     ON_PROMPT.md ON_UPDATE.md ON_WIP.md ON_CONFIGURE.md
    <project>-project/          the project bundle — the only place commands write
    <anything-else>/            background bundles — read-only

Dependencies: python 3.8+, stdlib only.
"""

import argparse
import json
import os
import re
import subprocess
import sys

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
    return f"{python} {rel(os.path.join(SKILL_DIR, 'context-db.py'))}"


# ── Config ───────────────────────────────────────────────────────────────────
# context-db.json is committed and shared. context-db.local.json is gitignored;
# any key it sets overrides the committed value for this user only.


def read_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def load_config(cdb):
    """Merged config, or None when context-db.json does not exist."""
    repo_path = os.path.join(cdb, CONFIG_NAME)
    if not os.path.isfile(repo_path):
        return None
    config = read_json(repo_path)
    local_path = os.path.join(cdb, LOCAL_CONFIG_NAME)
    if os.path.isfile(local_path):
        config.update(read_json(local_path))
    missing = [key for key in CONFIG_KEYS if key not in config]
    if missing:
        sys.exit(f"Error: {repo_path} is missing {', '.join(missing)}. Run /context-db configure.")
    return config


def require_config(cdb):
    config = load_config(cdb)
    if config is None:
        print(
            f"context-db is not configured for this repo: {os.path.join(cdb, CONFIG_NAME)} "
            "does not exist.\n\nTell the user, and offer to run `/context-db configure`. "
            "Do nothing else."
        )
        sys.exit(0)
    return config


def project_dir(cdb, config):
    return os.path.join(cdb, f"{config['project']}-project")


# ── Frontmatter ──────────────────────────────────────────────────────────────
# Hand-rolled, because the skill must run on a bare interpreter with no PyYAML.
# It reads top-level scalar keys only, in every scalar style an LLM produces:
# inline, quoted, folded onto continuation lines, or behind a block indicator.

KEY_RE = re.compile(r"^([A-Za-z_][\w-]*):(?:\s+(.*))?$")
BLOCK_SCALAR_RE = re.compile(r"^[>|][-+0-9]*$")


def parse_frontmatter(text):
    """Return (meta, body). meta is None when there is no frontmatter block."""
    lines = text.split("\n")
    if lines[0].strip() != "---":
        return None, text
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return None, text

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
    with open(path, "r", encoding="utf-8") as f:
        return parse_frontmatter(f.read())


def doc_title(path, meta, body):
    if meta and meta.get("title"):
        return meta["title"]
    for line in strip_code(body).split("\n"):
        if line.startswith("# "):
            return line[2:].strip()
    return os.path.splitext(os.path.basename(path))[0]


def strip_code(text):
    """Remove fenced code blocks and inline code so they are not scanned."""
    text = re.sub(r"(?ms)^[ \t]*(```|~~~).*?^[ \t]*\1[ \t]*$", "", text)
    return re.sub(r"`[^`\n]*`", "", text)


# ── Bundle walking ───────────────────────────────────────────────────────────


def visible(name):
    return not name.startswith(".")


def bundle_folders(bundle):
    """Every real folder in the bundle, root first. Symlinks are not followed."""
    folders = []
    for dirpath, dirnames, _ in os.walk(bundle):
        dirnames[:] = sorted(
            d for d in dirnames if visible(d) and not os.path.islink(os.path.join(dirpath, d))
        )
        folders.append(dirpath)
    return folders


def folder_files(folder):
    return sorted(
        name
        for name in os.listdir(folder)
        if visible(name) and name.endswith(".md") and os.path.isfile(os.path.join(folder, name))
    )


def folder_subfolders(folder):
    return sorted(
        name
        for name in os.listdir(folder)
        if visible(name)
        and os.path.isdir(os.path.join(folder, name))
        and not os.path.islink(os.path.join(folder, name))
    )


def descriptor_path(folder):
    """A folder is described by <folder>/<folder>.md.

    A mounted bundle may be symlinked under a different name than it has in the
    repo that owns it, so the real name is tried first.
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


def status_tag(meta):
    status = meta.get("status", "")
    return f" [{status}]" if status and status != "stable" else ""


# ── Index generation ─────────────────────────────────────────────────────────
# index.md is OKF's progressive-disclosure file: one line per child, each with
# its description. It is derived entirely from frontmatter, so it is generated
# and never edited by hand.


def index_entry(title, target, description):
    line = f"* [{title}]({target})"
    return f"{line} - {description}" if description else line


def build_index(folder, is_root):
    descriptor = descriptor_path(folder)
    sub_lines = []
    for name in folder_subfolders(folder):
        sub = os.path.join(folder, name)
        sub_lines.append(index_entry(name, f"{name}/index.md", folder_description(sub)))

    file_lines = []
    for name in folder_files(folder):
        if name in RESERVED_FILES:
            continue
        path = os.path.join(folder, name)
        meta, body = read_doc(path)
        if descriptor and os.path.samefile(path, descriptor) and not body.strip():
            continue  # a frontmatter-only descriptor is shown by the parent index
        meta = meta or {}
        description = meta.get("description", "") + status_tag(meta)
        file_lines.append(index_entry(doc_title(path, meta, body), name, description.strip()))

    parts = []
    if is_root:
        parts.append(f'---\nokf_version: "{OKF_VERSION}"\n---')
    if sub_lines:
        parts.append("# Subfolders\n\n" + "\n".join(sub_lines))
    if file_lines:
        parts.append("# Files\n\n" + "\n".join(file_lines))
    return "\n\n".join(parts) + "\n"


def sync_indexes(bundle, check):
    """Write (or, with check, compare) every index.md. Returns the stale paths."""
    stale = []
    for folder in bundle_folders(bundle):
        path = os.path.join(folder, "index.md")
        wanted = build_index(folder, folder == bundle)
        current = None
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as f:
                current = f.read()
        if current == wanted:
            continue
        stale.append(path)
        if not check:
            with open(path, "w", encoding="utf-8") as f:
                f.write(wanted)
    return stale


# ── Lint ─────────────────────────────────────────────────────────────────────

LINK_RE = re.compile(r"\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")


def lint_links(path, body):
    problems = []
    for target in LINK_RE.findall(strip_code(body)):
        if SCHEME_RE.match(target) or target.startswith("#"):
            continue
        target = target.split("#")[0]
        if target.startswith("/"):
            problems.append(f"{path}: link `{target}` is root-relative — use a file-relative link")
        elif not os.path.exists(os.path.join(os.path.dirname(path), target)):
            problems.append(f"{path}: broken link `{target}`")
    return problems


def lint_bundle(bundle):
    """Return (errors, warnings) for one bundle."""
    errors, warnings = [], []
    wip = os.path.join(bundle, "wip")
    for dirpath, dirnames, _ in os.walk(bundle):
        for name in sorted(dirnames):
            if os.path.islink(os.path.join(dirpath, name)):
                errors.append(
                    f"{os.path.join(dirpath, name)}: symlink inside a bundle — "
                    f"mount shared folders at the top level of {CONTEXT_DB}/ instead"
                )
        dirnames[:] = [d for d in dirnames if visible(d)]

    for folder in bundle_folders(bundle):
        files = [name for name in folder_files(folder) if name not in RESERVED_FILES]
        if not descriptor_path(folder):
            name = os.path.basename(folder)
            errors.append(f"{folder}/: no folder descriptor — add {name}.md with a description")
        items = len(files) + len(folder_subfolders(folder))
        if items > MAX_FOLDER_ITEMS:
            warnings.append(f"{folder}/: {items} items — split into subfolders (aim for 5–10)")

        for name in files:
            path = os.path.join(folder, name)
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
            meta, body = parse_frontmatter(text)
            if meta is None:
                errors.append(f"{path}: no YAML frontmatter")
                continue
            for key in ("type", "description"):
                if not meta.get(key):
                    errors.append(f"{path}: frontmatter has no `{key}`")
            status = meta.get("status", "")
            if status and status not in STATUSES:
                errors.append(f"{path}: status `{status}` is not one of {', '.join(STATUSES)}")
            errors.extend(lint_links(path, body))
            lines = text.count("\n")
            in_wip = os.path.commonpath([wip, path]) == wip
            if lines > MAX_FILE_LINES and not in_wip:
                warnings.append(
                    f"{path}: {lines} lines — split into a subfolder (max {MAX_FILE_LINES})"
                )
    return errors, warnings


# ── Prompt composition ───────────────────────────────────────────────────────


def load_prompt(name, **values):
    """Load prompts/<name>.md and fill its {placeholders}."""
    with open(os.path.join(SKILL_DIR, "prompts", f"{name}.md"), "r", encoding="utf-8") as f:
        text = f.read()
    for key, value in values.items():
        text = text.replace("{" + key + "}", str(value))
    return text.strip()


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


def instruction_section(instruction):
    if not instruction:
        return ""
    return f"# User Instruction\n\n{instruction.strip()}"


def bundles_section(cdb, config):
    """The mount listing: the project bundle first, then every background bundle.

    This is generated on every call rather than committed, because a user may
    mount private bundles through gitignored symlinks.
    """
    project = project_dir(cdb, config)
    lines = ["# Bundles", ""]

    def entry(label, folder):
        description = folder_description(folder) or "(no description)"
        index = os.path.join(folder, "index.md")
        if os.path.isfile(index):
            start = f"start at `{index}`"
        else:
            start = (
                "it has no `index.md`, so list the folder and read file frontmatter "
                "descriptions to find your way"
            )
        return f"- **{label}** `{folder}/` ({start}): {description}"

    if os.path.isdir(project):
        lines.append(entry("Project bundle", project))
    else:
        lines.append(f"- **Project bundle** `{project}/` is missing. Run `/context-db configure`.")

    for name in sorted(os.listdir(cdb)):
        folder = os.path.join(cdb, name)
        if (
            not visible(name)
            or name == ON_DIR_NAME
            or os.path.abspath(folder) == os.path.abspath(project)
        ):
            continue
        if os.path.islink(folder) and not os.path.exists(folder):
            lines.append(f"- Background bundle `{folder}/` is a broken symlink. Ignore it.")
        elif os.path.isdir(folder):
            lines.append(entry("Background bundle", folder))
    return "\n".join(lines)


def wip_files(wip):
    """(path, meta) for every wip document, descriptors and indexes excluded."""
    found = []
    if not os.path.isdir(wip):
        return found
    for folder in bundle_folders(wip):
        descriptor = descriptor_path(folder)
        for name in folder_files(folder):
            path = os.path.join(folder, name)
            if name in RESERVED_FILES or (descriptor and os.path.samefile(path, descriptor)):
                continue
            meta, _ = read_doc(path)
            found.append((path, meta or {}))
    return found


def wip_section(cdb, config, intro):
    wip = os.path.join(project_dir(cdb, config), "wip")
    files = wip_files(wip)
    lines = ["# Work In Progress", ""]
    if not files:
        lines.append(f"`{wip}/` is empty: no work in progress is recorded.")
        return "\n".join(lines)
    lines.append(intro)
    lines.append("")
    for path, meta in files:
        tags = status_tag(meta)
        if meta.get("branch"):
            tags += f" [branch: {meta['branch']}]"
        lines.append(f"- `{path}` — {meta.get('description', '(no description)')}{tags}")
    return "\n".join(lines)


def current_branch():
    return git("rev-parse", "--abbrev-ref", "HEAD").strip()


def capped(text, limit):
    lines = text.rstrip().split("\n")
    if len(lines) <= limit:
        return "\n".join(lines)
    return "\n".join(lines[:limit]) + f"\n... ({len(lines) - limit} more lines)"


def git_state_section(config):
    branch = current_branch()
    if not branch:
        return "# Git State\n\nNot a git repository, or git is unavailable."
    main = config["main_branch"]
    base = main if git("rev-parse", "--verify", "--quiet", main) else f"origin/{main}"
    lines = ["# Git State", "", f"- Current branch: `{branch}`", f"- Main branch: `{main}`"]

    def block(title, text, limit):
        text = text.strip("\n")
        lines.extend(
            ["", f"## {title}", "", "```", capped(text, limit) if text else "(none)", "```"]
        )

    block("Uncommitted changes (`git status --short`)", git("status", "--short"), 40)
    if branch == main:
        block("Recent commits", git("log", "--oneline", "-n", "15"), 15)
    else:
        block(
            f"Commits on `{branch}` not on `{main}`",
            git("log", "--oneline", f"{base}..HEAD"),
            40,
        )
        block(
            f"Files changed since `{main}`",
            git("diff", "--stat", f"{base}...HEAD"),
            60,
        )
    return "\n".join(lines)


# ── Commands ─────────────────────────────────────────────────────────────────


def cmd_prompt(args):
    cdb = context_db_dir()
    config = require_config(cdb)
    if not args.instruction:
        print("No instruction was given. Ask the user what they want to work on.")
        return
    branch = current_branch()
    on_branch = f" (the current branch is `{branch}`)" if branch else ""
    emit(
        [
            load_prompt("prompt", cdb=cdb, project_dir=project_dir(cdb, config)),
            bundles_section(cdb, config),
            wip_section(
                cdb,
                config,
                "These files describe the work happening right now. Read the ones that bear "
                f"on the instruction{on_branch} before anything else in the bundles.",
            ),
            on_file_text(cdb, "prompt"),
            instruction_section(args.instruction),
        ]
    )


def cmd_update(args):
    cdb = context_db_dir()
    config = require_config(cdb)
    commit = args.commit or args.push
    project = project_dir(cdb, config)
    nothing = (
        "say so, skip the rest of this section, and go straight to the Commit section"
        if commit
        else "tell the user there is nothing to add and stop"
    )
    sections = [
        load_prompt(
            "update",
            cdb=cdb,
            project_dir=project,
            on_dir=on_dir(cdb),
            index_cmd=f"{script_command(config['python'])} index",
            nothing_to_add=nothing,
        ),
        load_prompt("format"),
        on_file_text(cdb, "update"),
        instruction_section(args.instruction),
    ]
    if commit:
        push = "Then push the current branch to its remote." if args.push else "Do not push."
        sections.append(load_prompt("commit", cdb=cdb, push=push))
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
            wip_section(cdb, config, "Read every one of these files now."),
            load_prompt("format"),
            on_file_text(cdb, "wip"),
            instruction_section(args.instruction),
        ]
    )


def detect_main_branch():
    head = git("symbolic-ref", "--short", "refs/remotes/origin/HEAD").strip()
    if head.startswith("origin/"):
        return head[len("origin/") :]
    return current_branch() or "main"


def suggest_project_name(root):
    name = re.sub(r"[^a-z0-9]+", "-", os.path.basename(root).lower()).strip("-")
    return name or "my"


def v0_leftovers(root, cdb):
    """Signs that this repo still has the v0.0 layout."""
    found = []
    if os.path.isdir(cdb):
        found.extend(
            os.path.join(cdb, name)
            for name in sorted(os.listdir(cdb))
            if name.startswith("ON_") and name.endswith(".md")
        )
        for name in sorted(os.listdir(cdb)):
            old_wip = os.path.join(cdb, name, "wip.md")
            if name.endswith("-project") and os.path.isfile(old_wip):
                found.append(old_wip)
    old_scripts = os.path.join(root, ".claude", "skills", "context-db", "scripts")
    if os.path.isdir(old_scripts):
        found.append(rel(old_scripts) + "/")
    return found


def cmd_configure(args):
    root = find_repo_root()
    cdb = context_db_dir()
    repo_config = os.path.join(cdb, CONFIG_NAME)
    local_config = os.path.join(cdb, LOCAL_CONFIG_NAME)

    lines = ["# Detected State", ""]
    version = ".".join(str(part) for part in sys.version_info[:3])
    lines.append(f"- Interpreter running this script: `{sys.executable}` (Python {version})")
    lines.append(
        f"- Repository root: `{rel(root)}/` (suggested project name: `{suggest_project_name(root)}`)"
    )
    lines.append(f"- Detected main branch: `{detect_main_branch()}`")
    for label, path in (("Repo config", repo_config), ("User overrides", local_config)):
        if os.path.isfile(path):
            lines.append(f"- {label} `{path}`: `{json.dumps(read_json(path))}`")
        else:
            lines.append(f"- {label} `{path}`: does not exist")
    projects = []
    if os.path.isdir(cdb):
        projects = sorted(
            name
            for name in os.listdir(cdb)
            if name.endswith("-project") and os.path.isdir(os.path.join(cdb, name))
        )
    listed = ", ".join(f"`{os.path.join(cdb, name)}/`" for name in projects) or "none"
    lines.append(f"- Existing project bundles: {listed}")
    lines.append(
        f"- ON files folder `{on_dir(cdb)}/`: {'exists' if os.path.isdir(on_dir(cdb)) else 'does not exist'}"
    )
    leftovers = v0_leftovers(root, cdb)
    if leftovers:
        lines.append("")
        lines.append(
            "This repo still has the v0.0 layout (" + ", ".join(f"`{p}`" for p in leftovers) + "). "
            f"Follow the migration guide before step 2: {MIGRATION_GUIDE}"
        )

    python = (load_config(cdb) or {"python": "python3"})["python"]
    emit(
        [
            load_prompt(
                "configure",
                cdb=cdb,
                config_name=CONFIG_NAME,
                local_config_name=LOCAL_CONFIG_NAME,
                init_cmd=f"{script_command(python)} init",
                agents_snippet=rel(os.path.join(SKILL_DIR, "starters", "AGENTS.md")),
            ),
            "\n".join(lines),
            on_file_text(cdb, "configure"),
            instruction_section(args.instruction),
        ]
    )


def write_if_missing(path, text, created):
    if os.path.exists(path):
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    created.append(path)


def ignore_local_config(root, cdb):
    """Make sure the per-user override file can never be committed."""
    local = os.path.join(cdb, LOCAL_CONFIG_NAME)
    if not git("rev-parse", "--show-toplevel") or git("check-ignore", local).strip():
        return False
    entry = f"{CONTEXT_DB}/{LOCAL_CONFIG_NAME}"
    path = os.path.join(root, ".gitignore")
    existing = ""
    if os.path.isfile(path):
        with open(path, "r", encoding="utf-8") as f:
            existing = f.read()
    with open(path, "a", encoding="utf-8") as f:
        if existing and not existing.endswith("\n"):
            f.write("\n")
        f.write(f"{entry}\n")
    return True


def cmd_init(args):
    root = find_repo_root()
    cdb = context_db_dir()
    repo_path = os.path.join(cdb, CONFIG_NAME)
    local_path = os.path.join(cdb, LOCAL_CONFIG_NAME)
    os.makedirs(cdb, exist_ok=True)

    config = read_json(repo_path) if os.path.isfile(repo_path) else {}
    for key, value in (
        ("project", args.project),
        ("python", args.python),
        ("main_branch", args.main_branch),
    ):
        if value:
            config[key] = value
    if "project" not in config:
        sys.exit("Error: no project name. Pass --project <name>.")
    if "python" not in config:
        config["python"] = "python3"
    if "main_branch" not in config:
        config["main_branch"] = detect_main_branch()
    write_json(repo_path, config)
    print(f"Wrote {repo_path}: {json.dumps(config)}")

    if args.local:
        local = read_json(local_path) if os.path.isfile(local_path) else {}
        for item in args.local:
            key, separator, value = item.partition("=")
            if not separator or key not in CONFIG_KEYS:
                sys.exit(f"Error: --local takes key=value with key in {', '.join(CONFIG_KEYS)}.")
            local[key] = value
        write_json(local_path, local)
        print(f"Wrote {local_path}: {json.dumps(local)}")
    if ignore_local_config(root, cdb):
        print(f"Added {CONTEXT_DB}/{LOCAL_CONFIG_NAME} to .gitignore")

    created = []
    starters = os.path.join(SKILL_DIR, "starters")
    for command in ON_COMMANDS:
        name = f"ON_{command.upper()}.md"
        with open(os.path.join(starters, name), "r", encoding="utf-8") as f:
            write_if_missing(os.path.join(on_dir(cdb), name), f.read(), created)

    name = config["project"]
    project = project_dir(cdb, config)
    write_if_missing(
        os.path.join(project, f"{name}-project.md"),
        "---\ntype: Folder\ndescription:\n"
        f"  Main project folder for this repo — knowledge specific to {name}.\n---\n",
        created,
    )
    write_if_missing(
        os.path.join(project, "wip", "wip.md"),
        "---\ntype: Folder\ndescription:\n"
        "  Current work in progress — plans for what is being built right now. Files\n"
        "  here are deleted once the work lands.\n---\n",
        created,
    )
    for path in created:
        print(f"Created {path}")
    print()
    sys.exit(run_index(project, check=False))


def run_index(bundle, check):
    """Sync indexes, print the lint report, and return the exit code."""
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


def cmd_index(args):
    if args.bundle:
        bundle = os.path.normpath(args.bundle)
    else:
        cdb = context_db_dir()
        bundle = project_dir(cdb, require_config(cdb))
    if not os.path.isdir(bundle):
        sys.exit(f"Error: {bundle}/ is not a folder.")
    if os.path.islink(bundle):
        sys.exit(
            f"Error: {bundle} is a symlink to a bundle owned elsewhere. "
            "Run index in the repo that owns it."
        )
    sys.exit(run_index(bundle, args.check))


# ── CLI ──────────────────────────────────────────────────────────────────────


def build_parser():
    parser = argparse.ArgumentParser(
        prog="context-db",
        description="Project knowledge base: an OKF bundle plus the commands to use it.",
    )
    subs = parser.add_subparsers(dest="command", metavar="<command>")

    p = subs.add_parser("prompt", help="Consult the knowledge base for a piece of work")
    p.add_argument("instruction", nargs="?", default="")

    p = subs.add_parser("update", help="File a learning into the project bundle")
    p.add_argument("instruction", nargs="?", default="")
    p.add_argument("--commit", action="store_true", help="Then commit the whole session")
    p.add_argument("--push", action="store_true", help="Then commit and push")

    p = subs.add_parser("wip", help="Set up, refresh, and clean the work in progress")
    p.add_argument("instruction", nargs="?", default="")

    p = subs.add_parser("configure", help="Create or repair the config and scaffolding")
    p.add_argument("instruction", nargs="?", default="")

    p = subs.add_parser("init", help="(helper) Write the config and scaffold missing pieces")
    p.add_argument("--project", help="Project name; the bundle is context-db/<name>-project/")
    p.add_argument("--python", help="Interpreter command used to run this script")
    p.add_argument("--main-branch", help="Branch that work-in-progress is compared against")
    p.add_argument(
        "--local",
        action="append",
        metavar="KEY=VALUE",
        help=f"Per-user override written to {LOCAL_CONFIG_NAME} (repeatable)",
    )

    p = subs.add_parser("index", help="(helper) Regenerate index.md files and lint a bundle")
    p.add_argument(
        "bundle", nargs="?", default="", help="Bundle folder (default: the project bundle)"
    )
    p.add_argument("--check", action="store_true", help="Verify only; exit 1 if anything is off")

    subs.add_parser("help", help="Show this help message")
    return parser


def main():
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
