"""Tests for skill/context-db/context-db.py and the v0.0 migration script.

Every test runs the real script as a subprocess inside a throwaway project, the
way an agent would.
"""

import datetime
import importlib.util
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "skill" / "context-db" / "context-db.py"
MIGRATE = (
    REPO / "context-db" / "context-db-project" / "context-db-migrate-from-v0.0" / "migrate-v0.0.py"
)

sys.dont_write_bytecode = True  # keep __pycache__ out of the skill folder people copy
spec = importlib.util.spec_from_file_location("context_db", SCRIPT)
context_db = importlib.util.module_from_spec(spec)
spec.loader.exec_module(context_db)


def run(cwd, *args, script=SCRIPT, env=None):
    return subprocess.run(
        [sys.executable, str(script), *args],
        check=False,
        cwd=str(cwd),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
    )


def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def doc(type_name="Reference", description="A thing", extra="", body="# Title\n\nBody.\n"):
    return f"---\ntype: {type_name}\ndescription: {description}\n{extra}---\n\n{body}"


def git(cwd, *args):
    subprocess.run(
        ["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *args],
        cwd=str(cwd),
        check=True,
        stdout=subprocess.DEVNULL,
    )


@pytest.fixture
def project(tmp_path):
    """A minimal configured project with one document."""
    result = run(tmp_path, "configure", "--project", "demo", "--main-branch", "main")
    assert result.returncode == 0, result.stdout
    bundle = tmp_path / "context-db" / "demo-project"
    write(bundle / "retry-policy.md", doc("Convention", "Retry with backoff"))
    assert run(tmp_path, "toc", "--check").returncode == 0
    return tmp_path


@pytest.fixture
def example(tmp_path):
    """A copy of the example tree, symlinks preserved."""
    shutil.copytree(REPO / "example", tmp_path / "example", symlinks=True)
    target = tmp_path / "example" / "acme-payments-repo"
    skill_link = target / ".claude" / "skills" / "context-db"
    skill_link.unlink()
    skill_link.symlink_to(REPO / "skill" / "context-db")
    return target


# ── Frontmatter ──────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "header, expected",
    [
        ("description: plain value", "plain value"),
        ('description: "double quoted"', "double quoted"),
        ("description: 'single quoted'", "single quoted"),
        ("description:\n  folded onto\n  two lines", "folded onto two lines"),
        ("description: >\n  block folded\n  scalar", "block folded scalar"),
        ("description: >-\n  stripped block", "stripped block"),
        ("description: |\n  literal block", "literal block"),
        ("description: has: a colon inside", "has: a colon inside"),
    ],
)
def test_frontmatter_scalar_styles(header, expected):
    meta, body = context_db.parse_frontmatter(f"---\ntype: X\n{header}\n---\nbody\n")
    assert meta["description"] == expected
    assert meta["type"] == "X"
    assert body == "body\n"


def test_frontmatter_only_file_with_multiline_description():
    meta, body = context_db.parse_frontmatter("---\ntype: Folder\ndescription:\n  a\n  b\n---\n")
    assert meta == {"type": "Folder", "description": "a b"}
    assert body.strip() == ""


@pytest.mark.parametrize("content", ["# No frontmatter\n", "---\ntype: X\nnever closed\n", ""])
def test_missing_frontmatter_is_none(content):
    meta, body = context_db.parse_frontmatter(content)
    assert meta is None
    assert body == content


def test_nested_keys_do_not_become_top_level():
    meta, _ = context_db.parse_frontmatter(
        "---\ntype: X\ngenerated:\n  by: someone\n  at: now\ndescription: d\n---\n"
    )
    assert "by" not in meta
    assert meta["description"] == "d"


YAML_CASES = [
    "description: plain value",
    'description: "double quoted: with a colon"',
    "description: 'single quoted # not a comment'",
    "description:\n  folded onto\n  two lines",
    "description: >-\n  block: with a colon # and a hash",
    "description: |\n  literal: block",
    "description: has: a colon inside",
    "description: ends with a colon:",
    "description:\n  a line that ends with a colon:\n  and goes on",
    "description: has a # comment",
    "description: `backtick` start",
    'description: "unclosed quote',
    "description: 'it's wrong'",
    "description: 'it''s right'",
    "description: [bracket] start",
    "description: *star start",
    "description: - dash start",
    "description: -dash without a space is fine",
    "description: http://example.com/x is fine",
    "description: 10:30 is fine",
    'description: say "hi" in the middle',
    'description: "say \\"hi\\" escaped"',
    'description: "bad "inner" quotes"',
    "description: %percent start",
    "description: @at start",
    "description: {brace} start",
    "description: question? mark is fine",
    "description: ? question start",
    "description: a,b, c commas are fine",
    "description: 'padded'  ",
    "description:\n\tTab indented",
    "description: Refunds over $10,000 — approval & sign-off (finance)",
]


@pytest.mark.parametrize("case", YAML_CASES)
def test_the_yaml_check_agrees_with_a_real_yaml_parser(case):
    """A value passes the check exactly when PyYAML reads the same string we do."""
    yaml = pytest.importorskip("yaml")
    content = f"---\ntype: X\n{case}\n---\n"
    header = content.split("\n---", 1)[0][4:]
    meta, _ = context_db.parse_frontmatter(content)
    try:
        loaded = yaml.safe_load(header)
        expected = loaded["description"]
        real_yaml_agrees = isinstance(expected, str) and (
            " ".join(expected.split()) == " ".join(meta["description"].split())
        )
    except (yaml.YAMLError, KeyError, TypeError):
        real_yaml_agrees = False
    assert (not context_db.yaml_problems(content)) == real_yaml_agrees, case


def toc(cwd, folder="context-db/demo-project"):
    result = run(cwd, "toc", folder)
    assert result.returncode == 0, result.stdout
    return result.stdout


def test_byte_order_mark_and_bad_bytes_do_not_break_reading(project):
    bundle = project / "context-db" / "demo-project"
    (bundle / "bom.md").write_bytes(b"\xef\xbb\xbf" + doc(description="Has a BOM").encode())
    (bundle / "bytes.md").write_bytes(doc(description="Bad byte").encode() + b"\xff\xfe\n")
    assert run(project, "toc", "--check").returncode == 0
    listing = toc(project)
    assert "Has a BOM" in listing and "Bad byte" in listing


# ── Dynamic index (toc) ──────────────────────────────────────────────────────


def test_toc_lists_a_folder_from_its_files_as_they_are_now(project):
    listing = toc(project)
    assert listing.startswith("# Contents of `context-db/demo-project/`")
    assert "* [wip](context-db/demo-project/wip/) - Work in progress, if the project" in listing
    assert "* [Title](context-db/demo-project/retry-policy.md) - Retry with backoff" in listing
    write(project / "context-db" / "demo-project" / "new.md", doc(description="Brand new"))
    assert "(context-db/demo-project/new.md) - Brand new" in toc(project)
    assert toc(project) == run(project, "toc").stdout  # the project folder is the default


def test_toc_writes_nothing(project):
    before = sorted(str(p) for p in (project / "context-db").rglob("*"))
    toc(project)
    run(project, "toc", "--check")
    assert sorted(str(p) for p in (project / "context-db").rglob("*")) == before
    assert not list((project / "context-db").rglob("index.md"))


def test_toc_entries_follow_the_okf_index_shape(project):
    entry = re.compile(r"^\* \[.+\]\([^)\s]+\)( - .+)?$")
    body = toc(project).split("\n\n", 2)[2]
    for line in body.splitlines():
        assert not line or line in ("# Subfolders", "# Files") or entry.match(line), line


def test_frontmatter_only_descriptor_is_not_listed_but_one_with_body_is(project):
    bundle = project / "context-db" / "demo-project"
    assert "demo-project.md" not in toc(project)
    write(bundle / "demo-project.md", doc("Folder", "The demo", body="# Demo overview\n\nText.\n"))
    assert "* [Demo overview](context-db/demo-project/demo-project.md) - The demo" in toc(project)


def test_title_falls_back_from_frontmatter_to_h1_to_filename(project):
    bundle = project / "context-db" / "demo-project"
    write(bundle / "a.md", doc(extra="title: From Frontmatter\n"))
    write(bundle / "b.md", doc(body="```\n# not a heading\n```\n\n# From Heading\n"))
    write(bundle / "c.md", doc(body="No heading here.\n"))
    write(bundle / "d.md", doc(body="# Uses [brackets]\n"))
    listing = toc(project)
    assert "* [From Frontmatter](context-db/demo-project/a.md)" in listing
    assert "* [From Heading](context-db/demo-project/b.md)" in listing
    assert "* [c](context-db/demo-project/c.md)" in listing
    assert "* [Uses \\[brackets\\]](context-db/demo-project/d.md)" in listing


def test_non_stable_status_is_shown_in_the_listing(project):
    bundle = project / "context-db" / "demo-project"
    write(bundle / "old.md", doc(extra="status: deprecated\n"))
    write(bundle / "fine.md", doc(extra="status: stable\n"))
    listing = toc(project)
    assert "(context-db/demo-project/old.md) - A thing [deprecated]" in listing
    assert "(context-db/demo-project/fine.md) - A thing\n" in listing


def test_subfolder_entry_uses_the_descriptor_description(project):
    bundle = project / "context-db" / "demo-project"
    write(bundle / "api" / "api.md", "---\ntype: Folder\ndescription: HTTP API notes\n---\n")
    write(bundle / "api" / "errors.md", doc(description="Error codes"))
    assert "* [api](context-db/demo-project/api/) - HTTP API notes" in toc(project)
    sub = toc(project, "context-db/demo-project/api")
    assert "* [Title](context-db/demo-project/api/errors.md) - Error codes" in sub


def test_folders_without_markdown_are_not_part_of_the_tree(project):
    bundle = project / "context-db" / "demo-project"
    write(bundle / "images" / "diagram.svg", "<svg/>")
    write(bundle / "scripts" / "nested" / "tool.py", "print()\n")
    assert run(project, "toc", "--check").returncode == 0
    assert "images" not in toc(project) and "scripts" not in toc(project)


def test_an_empty_folder_says_so(project):
    empty = project / "context-db" / "demo-project" / "empty"
    write(empty / "empty.md", doc("Folder", "Nothing yet", body=""))
    assert "Nothing is in this folder yet." in toc(project, "context-db/demo-project/empty")


def test_toc_reads_through_a_mounted_folder(example):
    listing = toc(example, "context-db/coding-standards")
    assert listing.startswith("# Contents of `context-db/coding-standards/`")
    assert "context-db/coding-standards/" in listing.split("# Files")[1]
    result = run(example, "toc", "context-db/coding-standards", "--check")
    assert result.returncode == 0, result.stdout


def test_toc_works_on_any_folder_without_any_config(tmp_path):
    write(tmp_path / "shared" / "shared.md", "---\ntype: Folder\ndescription: Shared\n---\n")
    write(tmp_path / "shared" / "rule.md", doc())
    assert "* [Title](shared/rule.md) - A thing" in toc(tmp_path, "shared")
    assert run(tmp_path, "toc", "shared", "--check").returncode == 0


def test_toc_check_on_a_subfolder_checks_the_whole_bundle(project):
    write(project / "context-db" / "demo-project" / "bad.md", "# No frontmatter\n")
    result = run(project, "toc", "context-db/demo-project/wip", "--check")
    assert result.returncode == 1
    assert "checking all of context-db/demo-project/" in result.stdout
    assert "bad.md: no YAML frontmatter" in result.stdout
    assert "Fix them, then run:  python3 " in result.stdout and " toc --check" in result.stdout


def test_a_stray_index_file_is_an_error(project):
    write(project / "context-db" / "demo-project" / "index.md", "# Files\n")
    result = run(project, "toc", "--check")
    assert result.returncode == 1
    assert "index.md files are not used" in result.stdout
    assert "index.md" not in toc(project)


# ── Lint ─────────────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "name, content, message",
    [
        ("x.md", "# No frontmatter\n", "no YAML frontmatter"),
        ("x.md", "---\ndescription: d\n---\n", "no `type`"),
        ("x.md", "---\ntype: X\n---\n", "no `description`"),
        ("x.md", doc(extra="status: experiment\n"), "status `experiment`"),
        ("x.md", doc(description="Compliance rule: refunds"), "`description` is not valid YAML"),
        ("x.md", doc(description="`index.md` rules"), "it starts with ```"),
        ("x.md", doc(body="See [gone](./gone.md).\n"), "broken link `./gone.md`"),
        ("x.md", doc(body="See [root](/x.md).\n"), "starts with /"),
        ("sub/x.md", doc(), "no folder descriptor"),
    ],
)
def test_lint_errors(project, name, content, message):
    write(project / "context-db" / "demo-project" / name, content)
    result = run(project, "toc", "--check")
    assert result.returncode == 1
    assert message in result.stdout


def test_lint_ignores_links_in_code_and_external_links(project):
    bundle = project / "context-db" / "demo-project"
    write(bundle / "has space.md", doc())
    body = (
        "`[a](./gone.md)` and [site](https://example.com) and [anchor](#here) and\n"
        "[self](./retry-policy.md#section) and [encoded](./has%20space.md)\n\n"
        "```\n[b](./gone.md)\n```\n"
    )
    write(bundle / "x.md", doc(body=body))
    result = run(project, "toc", "--check")
    assert result.returncode == 0, result.stdout


def test_symlink_inside_a_bundle_is_an_error(project, tmp_path):
    (tmp_path / "elsewhere").mkdir(exist_ok=True)
    (project / "context-db" / "demo-project" / "linked").symlink_to(tmp_path / "elsewhere")
    result = run(project, "toc", "--check")
    assert result.returncode == 1
    assert "symlink inside a bundle" in result.stdout


def test_oversized_file_warns_but_wip_is_exempt(project):
    bundle = project / "context-db" / "demo-project"
    long_body = "# T\n\n" + "line\n" * 250
    write(bundle / "big.md", doc(body=long_body))
    write(bundle / "wip" / "plan.md", doc("Plan", body=long_body))
    result = run(project, "toc", "--check")
    assert result.returncode == 0
    assert "WARNING" in result.stdout and "big.md" in result.stdout
    assert "plan.md: 257 lines" not in result.stdout


# ── Things every command shares ──────────────────────────────────────────────


USER_COMMANDS = ("prompt", "update", "wip", "configure", "maintain")


def help_commands(out):
    """The command names --help lists, in order."""
    section = out.split("  <command>\n", 1)[1].split("\noptions:")[0]
    # A long name puts its help on the next line on older Pythons (3.8).
    return tuple(re.findall(r"(?m)^    (\w+)(?: |$)", section))


def test_version_and_help():
    assert run(REPO, "--version").stdout.strip() == "context-db 0.1 (OKF 0.2)"
    for args in ((), ("--help",)):
        assert help_commands(run(REPO, *args).stdout) == USER_COMMANDS
    assert run(REPO, "help").returncode != 0
    assert run(REPO, "init", "--project", "x").returncode != 0


def test_toc_runs_but_is_not_listed(project):
    assert "toc" not in help_commands(run(REPO, "--help").stdout)
    assert run(project, "toc", "--check").returncode == 0
    assert "read from the" in run(REPO, "toc", "--help").stdout
    assert run(REPO, "index").returncode != 0


def flat(markdown):
    return " ".join(markdown.replace("`", "").split())


def test_help_readme_and_docs_home_describe_the_commands_alike():
    """The one-line summaries in the script are the README table and the docs cards."""
    summaries = {name: flat(context_db.COMMAND_SUMMARIES[name]) for name in USER_COMMANDS}
    readme = (REPO / "README.md").read_text(encoding="utf-8")
    rows = re.findall(r"(?m)^\| `/context-db (\w+)` \| (.+?) \|$", readme)
    assert {name: flat(text) for name, text in rows} == summaries
    assert tuple(name for name, _ in rows) == USER_COMMANDS
    home = (REPO / "docs" / "index.md").read_text(encoding="utf-8")
    cards = re.findall(
        r"(?ms)^:::\{grid-item-card\} /context-db (\w+)\n(?::.*?\n)+\n(.+?)\n:::$", home
    )
    assert {name: flat(text) for name, text in cards} == summaries
    assert tuple(name for name, _ in cards) == USER_COMMANDS
    commands = (REPO / "docs" / "commands.md").read_text(encoding="utf-8")
    sections = tuple(re.findall(r"(?m)^## /context-db (\w+)$", commands))
    assert sections == USER_COMMANDS


def test_commands_without_config_ask_for_configure(tmp_path):
    (tmp_path / "context-db").mkdir()
    for command in ("prompt", "update", "wip"):
        result = run(tmp_path, command, "anything")
        assert result.returncode == 0
        assert "/context-db configure" in result.stdout


def test_broken_settings_are_reported_cleanly(project):
    settings = project / "context-db" / "configuration" / "settings.md"
    settings.write_text("project: demo\n")
    result = run(project, "prompt", "x")
    assert result.returncode != 0
    assert "has no `---` block" in result.stdout and "Traceback" not in result.stdout
    settings.write_text("---\nproject: demo\n---\n")
    result = run(project, "prompt", "x")
    assert result.returncode != 0
    assert "has no python, main_branch" in result.stdout


def test_no_placeholder_is_left_unfilled(example):
    for args in (
        ("prompt", "x"),
        ("update",),
        ("update", "x", "--push"),
        ("wip", "x"),
        ("wip", "--list"),
        ("wip", "--cleanup"),
        ("wip", "--clear"),
        ("maintain",),
        ("maintain", "data-model"),
        ("maintain", "--use-git-diff"),
        ("configure",),
    ):
        out = run(example, *args).stdout
        assert not re.findall(r"\{[a-z_]+\}", out), args


def test_an_unquoted_instruction_is_joined(project):
    out = run(project, "prompt", "add", "a", "refund", "endpoint").stdout
    assert out.rstrip().endswith("# User Instruction\n\nadd a refund endpoint")
    out = run(project, "update", "note", "this", "--push").stdout
    assert out.rstrip().endswith("note this")


def test_output_survives_an_ascii_only_stdout(project):
    env = dict(os.environ, PYTHONIOENCODING="ascii", PYTHONUTF8="0")
    for args in (("prompt", "x"), ("update",), ("wip",), ("wip", "--cleanup"), ("configure",)):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            check=False,
            cwd=str(project),
            env=env,
            capture_output=True,
        )
        assert result.returncode == 0, result.stderr


def test_paths_are_relative_to_the_callers_cwd(project):
    subprocess.run(["git", "init", "-q"], cwd=str(project), check=True)
    sub = project / "src"
    sub.mkdir()
    out = run(sub, "prompt", "x").stdout
    assert "`../context-db/demo-project/`" in out


# ── prompt ───────────────────────────────────────────────────────────────────


def test_prompt_without_instruction(project):
    assert "Ask the user" in run(project, "prompt").stdout


def test_prompt_lists_folders_and_wip_then_rules_then_instruction(example):
    out = run(example, "prompt", "add a refund endpoint").stdout
    assert "**Project folder** `context-db/acme-payments-project/`" in out
    assert "**Background folder** `context-db/coding-standards/`" in out
    assert "**Background folder** `context-db/git-standards/`:" in out
    wip = out.split("# Work In Progress")[1].split("# Folders")[0]
    assert "relative to\n`context-db/acme-payments-project/wip/`" in wip
    assert "- [Refund endpoint](refund-endpoint.md). Started 2026-11-03" in wip
    assert "configuration" not in out.split("# Folders")[1].split("# Project Rules")[0]
    marks = (
        "# Work In Progress",
        "# Folders",
        "# Project Rules",
        "PCI-scoped",
        "# User Instruction",
    )
    order = [out.index(mark) for mark in marks]
    assert order == sorted(order)
    assert out.rstrip().endswith("add a refund endpoint")
    assert "<!--" not in out


def test_prompt_leaves_out_an_empty_wip_list(project):
    assert "# Work In Progress" not in run(project, "prompt", "x").stdout
    shutil.rmtree(project / "context-db" / "demo-project" / "wip")
    assert "# Work In Progress" not in run(project, "prompt", "x").stdout


def test_prompt_handles_unindexed_and_broken_mounts(project):
    cdb = project / "context-db"
    write(cdb / "legacy" / "legacy.md", "---\ndescription: Old format folder\n---\n")
    (cdb / "dangling").symlink_to(project / "does-not-exist")
    out = run(project, "prompt", "x").stdout
    assert "**Background folder** `context-db/legacy/`:" in out
    assert "Old format folder" in out
    assert "`context-db/dangling/` is a broken symlink" in out


def test_mounted_folder_descriptor_is_found_under_its_real_name(project, tmp_path):
    source = tmp_path / "elsewhere" / "coding-standards"
    write(source / "coding-standards.md", "---\ntype: Folder\ndescription: Real name wins\n---\n")
    (project / "context-db" / "general-standards").symlink_to(source)
    assert "Real name wins" in run(project, "prompt", "x").stdout


# ── update ───────────────────────────────────────────────────────────────────


def test_update_puts_the_gate_before_the_mechanics(project):
    out = run(project, "update").stdout
    marks = ("nothing to add and stop", "## Where it goes", "# Folders", "# File Format")
    order = [out.index(mark) for mark in marks]
    assert order == sorted(order)
    assert "context-db.py toc --check" in out
    assert "# Commit" not in out
    assert "# User Instruction" not in out


def test_update_changes_only_what_the_lesson_needs(project):
    out = " ".join(run(project, "update").stdout.split())
    assert "change only what it needs" in out
    assert "that is what `/context-db maintain` is for" in out
    assert "If it reports problems in files you did not touch, leave them" in out


def test_update_carries_the_split_as_you_go_rule(project):
    out = " ".join(run(project, "update").stdout.split())
    rules = out.split("# Project Rules")[1]
    assert "When a file you are editing grows past about 150 lines, split it" in rules


def test_update_commit_and_push(project):
    commit = run(project, "update", "note this", "--commit").stdout
    assert "go straight to the Commit section" in commit
    assert commit.index("# Commit") < commit.index("# User Instruction")
    assert "Do not push." in commit
    assert commit.rstrip().endswith("note this")
    assert "Then push the current branch" in run(project, "update", "--push").stdout


def test_on_file_is_inlined_without_comments_or_frontmatter(project):
    write(
        project / "context-db" / "configuration" / "ON_UPDATE.md",
        "---\ndescription: ignored\n---\n<!-- hidden\nnote -->\nAlways cite the ticket.\n",
    )
    out = run(project, "update", "--commit").stdout
    assert "Always cite the ticket." in out
    assert out.index("# Commit") < out.index("Always cite the ticket.")
    assert "hidden" not in out and "ignored" not in out


def test_on_rules_keep_a_heading_the_author_wrote(project):
    on_file = project / "context-db" / "configuration" / "ON_PROMPT.md"
    write(on_file, "<!-- note -->\nBe careful.\n")
    assert "# Project Rules\n\nBe careful." in run(project, "prompt", "x").stdout
    write(on_file, "# House Rules\n\nBe careful.\n")
    out = run(project, "prompt", "x").stdout
    assert "# House Rules\n\nBe careful." in out and "# Project Rules" not in out
    write(on_file, "<!-- only a comment -->\n")
    assert "# Project Rules" not in run(project, "prompt", "x").stdout


def test_an_instruction_can_come_from_standard_input(project):
    tricky = "Don't retry refunds over $10,000; they aren't \"idempotent\" & `fail`"
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "update", "-", "--push"],
        check=False,
        cwd=str(project),
        input=tricky + "\n",
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.rstrip().endswith("# User Instruction\n\n" + tricky)
    assert "Then push the current branch" in result.stdout


def test_printed_commands_use_the_local_interpreter_override(project):
    assert run(project, "configure", "--local", "python=/opt/py/bin/python3").returncode == 0
    assert "/opt/py/bin/python3 " in run(project, "update").stdout
    assert "/opt/py/bin/python3 " in run(project, "wip").stdout
    assert "/opt/py/bin/python3 " in run(project, "configure").stdout
    conf = project / "context-db" / "configuration"
    assert "python: python3\n" in (conf / "settings.md").read_text()
    local = (conf / "settings.local.md").read_text()
    assert local.startswith("---\npython: /opt/py/bin/python3\n---\n")


# ── maintain ─────────────────────────────────────────────────────────────────


def test_maintain_checks_first_and_can_stop(project):
    write(
        project / "context-db" / "configuration" / "ON_MAINTAIN.md",
        "<!-- note -->\nNever delete anything under legal/.\n",
    )
    out = run(project, "maintain", "the api notes").stdout
    flat_out = " ".join(out.split())
    assert "Check first, change second." in flat_out
    assert "If you find nothing worth changing, say so in one line and stop." in flat_out
    assert "context-db.py toc --check" in out
    assert "**Project folder** `context-db/demo-project/`" in out
    marks = ("# Context-db Maintain", "# Folders", "# File Format", "legal/", "# User Instruction")
    order = [out.index(mark) for mark in marks]
    assert order == sorted(order)
    assert out.rstrip().endswith("the api notes")


def test_maintain_without_config_asks_for_configure(tmp_path):
    (tmp_path / "context-db").mkdir()
    assert "/context-db configure" in run(tmp_path, "maintain").stdout


RULE = "# Context-db Is Not a Mirror of the Code"


def test_every_command_that_reads_or_writes_notes_repeats_the_rule(project):
    for args in (("prompt", "x"), ("update",), ("maintain",), ("wip",), ("wip", "--cleanup")):
        out = run(project, *args).stdout
        assert out.count(RULE) == 1, args
        assert "could an agent learn this by reading the code and its\ncomments?" in out
    for args in (("wip", "--list"), ("configure",)):
        assert RULE not in run(project, *args).stdout


def test_every_command_that_reads_notes_says_how_to_navigate(project):
    for args in (("prompt", "x"), ("update",), ("maintain",), ("wip",), ("wip", "--cleanup")):
        out = run(project, *args).stdout
        assert out.count("# How to Navigate Context-db") == 1, args
        assert "context-db.py toc <folder>" in out, args
    prompts = REPO / "skill" / "context-db" / "prompts"
    mentions = sorted(p.name for p in prompts.glob("*.md") if "index.md" in p.read_text())
    assert mentions == ["format.md"]  # only to say: never create one


def test_maintain_enforces_the_rule_against_code_and_comments(project):
    out = " ".join(run(project, "maintain").stdout.split())
    assert "Your main job is to enforce the rule" in out
    assert "open the code it is about, comments included" in out
    assert "do not edit the code yourself" in out
    assert "# Git History" not in out


def test_maintain_with_git_diff_ranks_notes_by_how_far_the_code_moved(project):
    bundle = project / "context-db" / "demo-project"
    write(project / "src" / "retry.py", "DELAY = 1\n")
    write(
        bundle / "retry-policy.md",
        doc("Convention", "Retry", body="See [retry](../../src/retry.py).\n"),
    )
    write(bundle / "naming.md", doc("Convention", "Naming"))
    git(project, "init", "-q", "-b", "main")
    git(project, "add", "-A")
    git(project, "commit", "-q", "-m", "base")
    write(project / "src" / "retry.py", "DELAY = 2\n")
    write(project / "src" / "other.py", "x = 1\n")
    git(project, "add", "-A")
    git(project, "commit", "-q", "-m", "code moves on")
    write(bundle / "fresh.md", doc("Reference", "New"))
    out = run(project, "maintain", "--use-git-diff").stdout
    history = out.split("# Git History")[1].split("# Folders")[0]
    rows = [line for line in history.splitlines() if line.startswith("- `")]
    assert "retry-policy.md`: last changed" in rows[0]
    assert "1 commits to the project since; linked files changed since: `src/retry.py`" in rows[0]
    assert "naming.md`" in rows[1] and "linked files" not in rows[1]
    assert rows[-1].endswith("fresh.md`: not committed yet")
    assert "Age alone proves nothing." in history
    assert out.index(RULE) < out.index("# Git History") < out.index("# Folders")


def test_maintain_with_git_diff_outside_git(project):
    assert "no history to read" in run(project, "maintain", "--use-git-diff").stdout


# ── wip ──────────────────────────────────────────────────────────────────────


def add_plan(project, name="x-plan", line=None):
    wip = project / "context-db" / "demo-project" / "wip"
    if line is None:
        write(wip / f"{name}.md", doc("Plan", f"The {name}", extra="branch: feature/x\n"))
    listing = wip / "wip.md"
    item = line or f"- [{name}]({name}.md). Started 2026-11-01 on `feature/x`. Half done."
    heading = "# Work in progress\n"
    listing.write_text(listing.read_text().replace(heading, f"{heading}\n{item}\n"))


def test_wip_records_the_current_work(project):
    git(project, "init", "-q", "-b", "main")
    git(project, "add", "-A")
    git(project, "commit", "-q", "-m", "base")
    git(project, "checkout", "-q", "-b", "feature/x")
    add_plan(project)
    out = run(project, "wip", "plan the x work").stdout
    flat = " ".join(out.split())
    assert "It is optional" in flat
    assert "today, " + datetime.date.today().isoformat() + ", on `feature/x`" in flat
    assert "- [x-plan](x-plan.md). Started 2026-11-01" in out
    assert "# How Work In Progress Is Kept" in out and "# File Format" in out
    assert "# Git State" not in out
    assert out.rstrip().endswith("plan the x work")


def test_wip_cleanup_shows_git_state_and_the_list(project):
    git(project, "init", "-q", "-b", "main")
    git(project, "add", "-A")
    git(project, "commit", "-q", "-m", "base")
    git(project, "checkout", "-q", "-b", "feature/x")
    write(project / "src.py", "print('hi')\n")
    git(project, "add", "-A")
    git(project, "commit", "-q", "-m", "add src")
    add_plan(project)
    out = run(project, "wip", "--cleanup").stdout
    assert "# Context-db Wip Cleanup" in out
    assert "- Current branch: `feature/x`" in out
    assert "- Main branch: `main`" in out
    assert "Work has landed when it is merged into `main`" in out
    assert "add src" in out and "src.py" in out
    assert "x-plan.md" in out.split("git status --short")[1]
    assert "- [x-plan](x-plan.md)" in out.split("# Work In Progress")[1]


def test_wip_list_only_shows_the_list(project):
    add_plan(project)
    out = run(project, "wip", "--list").stdout
    assert "Today is " + datetime.date.today().isoformat() in out
    assert "Read nothing else and change nothing." in out
    assert "- [x-plan](x-plan.md). Started 2026-11-01" in out
    assert "# Git State" not in out and "# File Format" not in out
    assert "# How Work In Progress Is Kept" not in out


def test_wip_clear_asks_before_deleting(project):
    add_plan(project)
    out = run(project, "wip", "--clear").stdout
    assert "Ask the user to confirm. Stop if they do not." in out
    assert "# Git State" not in out


def test_wip_flags_are_exclusive(project):
    result = run(project, "wip", "--list", "--clear")
    assert result.returncode != 0 and "not allowed with" in result.stdout


def test_wip_with_nothing_listed_says_so(project):
    out = run(project, "wip", "--list").stdout
    assert "lists nothing: no work in progress is recorded" in out


def test_wip_on_the_main_branch_shows_recent_commits(project):
    git(project, "init", "-q", "-b", "main")
    git(project, "add", "-A")
    git(project, "commit", "-q", "-m", "only commit")
    out = run(project, "wip", "--cleanup").stdout
    assert "## Recent commits" in out and "only commit" in out


def test_wip_says_so_when_the_main_branch_does_not_exist(project):
    git(project, "init", "-q", "-b", "trunk")
    git(project, "add", "-A")
    git(project, "commit", "-q", "-m", "base")
    out = run(project, "wip", "--cleanup").stdout
    assert "main branch `main` does not exist" in out
    assert "context-db/configuration/settings.md" in out
    assert "base" in out


def test_wip_outside_git(project):
    assert "Not a git repository" in run(project, "wip", "--cleanup").stdout


def test_plans_missing_from_the_list_are_reported(project):
    wip = project / "context-db" / "demo-project" / "wip"
    write(wip / "stray.md", doc("Plan", "Forgotten"))
    write(wip / "big" / "big.md", doc("Plan", "Large effort"))
    out = run(project, "toc", "--check").stdout
    assert "wip/stray.md: not listed in" in out and "wip/big: not listed in" in out
    add_plan(project, "stray")
    add_plan(project, "big", line="- [Big](big/big.md). Started 2026-11-01 on `x`. Going.")
    assert "not listed" not in run(project, "toc", "--check").stdout


# ── configure ──────────────────────────────────────────────────────────────────


def test_configure_says_when_the_main_branch_is_a_guess(tmp_path):
    out = run(tmp_path, "configure").stdout
    assert "Suggested main branch: `main` (a guess: nothing could be detected)" in out
    git(tmp_path, "init", "-q", "-b", "trunk")
    write(tmp_path / "a.txt", "x\n")
    git(tmp_path, "add", "-A")
    git(tmp_path, "commit", "-q", "-m", "base")
    out = run(tmp_path, "configure").stdout
    assert "Suggested main branch: `trunk` (a guess: the branch checked out now" in out
    git(tmp_path, "update-ref", "refs/remotes/origin/develop", "HEAD")
    git(tmp_path, "symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/develop")
    out = run(tmp_path, "configure").stdout
    assert "Suggested main branch: `develop` (origin's default branch)" in out


def test_configure_reports_state_and_v0_leftovers(tmp_path):
    write(tmp_path / "context-db" / "ON_PROMPT.md", "old\n")
    write(tmp_path / "context-db" / "acme-project" / "wip.md", "old\n")
    out = run(tmp_path, "configure").stdout
    assert "settings.md`: does not exist" in out
    assert "`AGENTS.md`: does not exist" in out
    assert "`context-db/acme-project/`" in out
    assert "Suggested project name: `acme` (from the existing project folder)" in out
    assert "v0.0 layout" in out and "ON_PROMPT.md" in out and "wip.md" in out
    assert " configure --project <name>" in out


def test_configure_still_runs_when_the_settings_are_broken(project):
    settings = project / "context-db" / "configuration" / "settings.md"
    for broken in ("project: demo", "---\nproject: demo\n---\n", ""):
        settings.write_text(broken)
        result = run(project, "configure")
        assert result.returncode == 0, result.stdout
        assert "# Detected State" in result.stdout
    settings.write_text("no frontmatter")
    assert "has no `---` block" in run(project, "configure").stdout


def test_configure_with_settings_scaffolds_and_never_overwrites(tmp_path):
    subprocess.run(["git", "init", "-q"], cwd=str(tmp_path), check=True)
    result = run(
        tmp_path,
        "configure",
        "--main-branch",
        "trunk",
        "--python",
        "python3.11",
        "--project",
        "demo",
    )
    assert result.returncode == 0, result.stdout
    cdb = tmp_path / "context-db"
    settings = cdb / "configuration" / "settings.md"
    assert settings.read_text().startswith(
        "---\nproject: demo\npython: python3.11\nmain_branch: trunk\n---\n\n<!--\n"
    )
    for name in (
        "ON_PROMPT.md",
        "ON_UPDATE.md",
        "ON_MAINTAIN.md",
        "ON_WIP.md",
        "ON_CONFIGURE.md",
    ):
        assert (cdb / "configuration" / name).exists()
    assert (cdb / "demo-project" / "demo-project.md").exists()
    assert (cdb / "demo-project" / "wip" / "wip.md").read_text().startswith("---\ntype: Folder\n")
    gitignore = (tmp_path / ".gitignore").read_text()
    assert "context-db/configuration/settings.local.md" in gitignore

    write(cdb / "configuration" / "ON_PROMPT.md", "mine\n")
    settings.write_text(settings.read_text() + "\nA note of my own.\n")
    again = run(tmp_path, "configure", "--main-branch", "main")
    assert again.returncode == 0
    assert (cdb / "configuration" / "ON_PROMPT.md").read_text() == "mine\n"
    content = settings.read_text()
    assert "main_branch: main\n" in content and "python: python3.11\n" in content
    assert content.endswith("A note of my own.\n")
    assert (tmp_path / ".gitignore").read_text().count("settings.local.md") == 1


def test_the_starter_rules_let_the_agent_update_as_it_goes(tmp_path):
    assert run(tmp_path, "configure", "--project", "demo").returncode == 0
    out = run(tmp_path, "prompt", "x").stdout
    assert "You may update the knowledge base as you work" in out
    assert "context-db.py update '<what you learned>'" in out
    assert "<!--" not in out and "{update_cmd}" not in out


def test_configure_asks_the_questions_that_matter(tmp_path):
    out = " ".join(run(tmp_path, "configure").stdout.split())
    assert "AskUserQuestion" in out
    assert "`/context-db configure` is a helper" in out
    assert "sweeping changes that break backwards compatibility" in out
    assert "only when you run a `/context-db` command?" in out
    assert "may the agent update the knowledge base as it works?" in out
    assert "edit them by hand" in out
    assert " configure --project <name> --main-branch <branch> --python <command>" in out
    assert "split it up as it goes, or only when you run `/context-db maintain`?" in out
    assert "The user runs it first" in out
    assert "context-db.py update '<what you learned>'" in out


def test_configure_shows_the_current_rules_so_they_can_be_changed(project):
    on = project / "context-db" / "configuration"
    write(on / "ON_UPDATE.md", "<!-- note -->\nCommit messages follow Conventional Commits.\n")
    out = run(project, "configure").stdout
    rules = out.split("# Current Rules")[1]
    assert "ON_UPDATE.md`, added to every `/context-db update`" in rules
    assert "Commit messages follow Conventional Commits." in rules
    assert "You may update the knowledge base as you work" in rules
    assert "ON_WIP.md`, added to every `/context-db wip`\n\n(empty: it adds nothing)" in rules
    assert "begin by asking what the user wants to do" in out
    assert "Does this project rely on other repositories?" in out
    assert "**This was a helper.**" in out


def test_configure_with_settings_rejects_bad_input_without_writing_anything(tmp_path):
    for args in (
        ("--main-branch", "main"),
        ("--project", "has space"),
        ("--project", "a/b"),
        ("--project", "demo", "--local", "colour=blue"),
        ("--project", "demo", "--local", "python"),
    ):
        assert run(tmp_path, "configure", *args).returncode != 0
    assert not (tmp_path / "context-db").exists()


def test_configure_with_settings_catches_a_project_name_given_with_its_suffix(tmp_path):
    write(tmp_path / "context-db" / "acme-project" / "acme-project.md", doc("Folder", "Acme"))
    result = run(tmp_path, "configure", "--project", "acme-project")
    assert result.returncode != 0
    assert "--project acme" in result.stdout
    assert not (tmp_path / "context-db" / "acme-project-project").exists()


# ── The shipped trees stay clean ─────────────────────────────────────────────


def test_example_project_and_shared_folders_are_conformant(example):
    assert run(example, "toc", "--check").returncode == 0
    shared = example.parent / "shared"
    for name in ("coding-standards", "git-standards"):
        result = run(shared, "toc", name, "--check")
        assert result.returncode == 0, result.stdout


def test_this_repos_own_knowledge_base_is_conformant():
    result = run(REPO, "toc", "--check")
    assert result.returncode == 0, result.stdout


def shipped_documents():
    roots = [
        REPO / "context-db" / "context-db-project",
        REPO / "example" / "acme-payments-repo" / "context-db" / "acme-payments-project",
        REPO / "example" / "shared",
    ]
    return [path for root in roots for path in sorted(root.rglob("*.md"))]


def test_frontmatter_is_real_yaml_and_the_parser_agrees_with_a_yaml_library():
    """OKF asks for parseable YAML, so check with an independent parser."""
    yaml = pytest.importorskip("yaml")
    for path in shipped_documents():
        content = path.read_text(encoding="utf-8")
        assert content.startswith("---\n"), path
        expected = yaml.safe_load(content.split("\n---", 1)[0][4:])
        meta, _ = context_db.parse_frontmatter(content)
        assert isinstance(expected["type"], str) and expected["type"], path
        for key in ("type", "description", "status", "branch"):
            if key in expected:
                assert meta[key] == " ".join(str(expected[key]).split()), (path, key)


# ── Migration from v0.0 ──────────────────────────────────────────────────────


def test_migrating_a_v0_tree_ends_lint_clean(tmp_path):
    cdb = tmp_path / "context-db"
    bundle = cdb / "acme-project"
    write(cdb / "ON_PROMPT.md", "---\ndescription: d\n---\nBe careful.\n")
    write(cdb / "ON_MAINTAIN.md", "old\n")
    write(bundle / "acme-project.md", "---\ndescription: Acme\n---\n")
    write(
        bundle / "wip.md", "---\ndescription: Active work\n---\n\n# WIP\n\nSee `./standards.md`.\n"
    )
    write(
        bundle / "design-decisions.md",
        "---\ndescription: Why we queue\nstatus: experiment\n---\n\n"
        "# Decisions\n\nSee `./standards.md`, `standards.md`, `README.md` and `./missing.md`.\n\n"
        "```\n`./standards.md`\n```\n",
    )
    write(bundle / "standards.md", "---\ndescription: Coding standards\n---\n\n# Standards\n")
    write(bundle / "api" / "api-instructions.md", "---\ndescription: API notes\n---\n")
    write(
        bundle / "api" / "errors.md",
        "---\ndescription: Error codes\n---\n\nFollows `standards.md`. Run the TOC script.\n",
    )

    dry = run(tmp_path, "context-db", "--dry-run", script=MIGRATE)
    assert dry.returncode == 0 and (cdb / "ON_PROMPT.md").exists()
    assert "type:" not in (bundle / "standards.md").read_text()

    result = run(tmp_path, "context-db", script=MIGRATE)
    assert result.returncode == 0, result.stdout
    assert (cdb / "configuration" / "ON_PROMPT.md").exists()
    plan = (bundle / "wip" / "current-work.md").read_text()
    assert plan.startswith("---\ntype: Plan\n")
    assert "[standards.md](../standards.md)" in plan
    assert (bundle / "wip" / "wip.md").read_text().startswith("---\ntype: Folder\n")
    assert "Follows [standards.md](../standards.md)." in (bundle / "api" / "errors.md").read_text()
    mentions = result.stdout.split("Mentions of v0.0 machinery")[1]
    assert "api/errors.md:6: `TOC script`" in mentions
    decide = result.stdout.split("Needs a decision")[1].split("## Mentions")[0]
    assert (cdb / "configuration" / "ON_MAINTAIN.md").exists()
    assert "`./missing.md` does not resolve" in decide
    assert "rename api-instructions.md to api.md" in decide

    decisions = (bundle / "design-decisions.md").read_text()
    assert decisions.startswith("---\ntype: Decision\n")
    assert "status: draft" in decisions
    assert (
        "See [standards.md](./standards.md), [standards.md](standards.md), `README.md`" in decisions
    )
    assert "```\n`./standards.md`\n```" in decisions
    assert (bundle / "acme-project.md").read_text().startswith("---\ntype: Folder\n")
    assert (bundle / "standards.md").read_text().startswith("---\ntype: Convention\n")

    again = run(tmp_path, "context-db", script=MIGRATE)
    assert again.stdout.split("## Types guessed")[0].strip().endswith("(nothing)")
    assert "wip" not in again.stdout.split("Needs a decision")[1].split("## Mentions")[0]

    (bundle / "api" / "api-instructions.md").rename(bundle / "api" / "api.md")
    init = run(tmp_path, "configure", "--project", "acme")
    assert init.returncode == 0, init.stdout
    assert "Be careful." in run(tmp_path, "prompt", "x").stdout
    assert not list(bundle.rglob("index.md"))
