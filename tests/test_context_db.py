"""Tests for skill/context-db/context-db.py and the v0.0 migration script.

Every test runs the real script as a subprocess inside a throwaway project, the
way an agent would.
"""

import importlib.util
import json
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
    result = run(tmp_path, "init", "--project", "demo", "--main-branch", "main")
    assert result.returncode == 0, result.stdout
    bundle = tmp_path / "context-db" / "demo-project"
    write(bundle / "retry-policy.md", doc("Convention", "Retry with backoff"))
    assert run(tmp_path, "index").returncode == 0
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


def test_byte_order_mark_and_bad_bytes_do_not_break_reading(project):
    bundle = project / "context-db" / "demo-project"
    (bundle / "bom.md").write_bytes(b"\xef\xbb\xbf" + doc(description="Has a BOM").encode())
    (bundle / "bytes.md").write_bytes(doc(description="Bad byte").encode() + b"\xff\xfe\n")
    result = run(project, "index")
    assert result.returncode == 0, result.stdout
    index = (bundle / "index.md").read_text(encoding="utf-8")
    assert "Has a BOM" in index and "Bad byte" in index


# ── Index generation ─────────────────────────────────────────────────────────


def test_root_index_declares_okf_version_and_lists_children(project):
    index = (project / "context-db" / "demo-project" / "index.md").read_text()
    assert index.startswith('---\nokf_version: "0.2"\n---\n')
    assert "* [wip](wip/index.md) - Current work in progress" in index
    assert "* [Title](retry-policy.md) - Retry with backoff" in index


def test_frontmatter_only_descriptor_is_not_listed_but_one_with_body_is(project):
    bundle = project / "context-db" / "demo-project"
    assert "demo-project.md" not in (bundle / "index.md").read_text()
    write(bundle / "demo-project.md", doc("Folder", "The demo", body="# Demo overview\n\nText.\n"))
    run(project, "index")
    assert "* [Demo overview](demo-project.md) - The demo" in (bundle / "index.md").read_text()


def test_title_falls_back_from_frontmatter_to_h1_to_filename(project):
    bundle = project / "context-db" / "demo-project"
    write(bundle / "a.md", doc(extra="title: From Frontmatter\n"))
    write(bundle / "b.md", doc(body="```\n# not a heading\n```\n\n# From Heading\n"))
    write(bundle / "c.md", doc(body="No heading here.\n"))
    write(bundle / "d.md", doc(body="# Uses [brackets]\n"))
    run(project, "index")
    index = (bundle / "index.md").read_text()
    assert "* [From Frontmatter](a.md)" in index
    assert "* [From Heading](b.md)" in index
    assert "* [c](c.md)" in index
    assert "* [Uses \\[brackets\\]](d.md)" in index


def test_non_stable_status_is_shown_in_the_index(project):
    bundle = project / "context-db" / "demo-project"
    write(bundle / "old.md", doc(extra="status: deprecated\n"))
    write(bundle / "fine.md", doc(extra="status: stable\n"))
    run(project, "index")
    index = (bundle / "index.md").read_text()
    assert "(old.md) - A thing [deprecated]" in index
    assert "(fine.md) - A thing\n" in index


def test_subfolder_entry_uses_the_descriptor_description(project):
    bundle = project / "context-db" / "demo-project"
    write(bundle / "api" / "api.md", "---\ntype: Folder\ndescription: HTTP API notes\n---\n")
    write(bundle / "api" / "errors.md", doc(description="Error codes"))
    assert run(project, "index").returncode == 0
    assert "* [api](api/index.md) - HTTP API notes" in (bundle / "index.md").read_text()
    sub = (bundle / "api" / "index.md").read_text()
    assert "okf_version" not in sub
    assert "* [Title](errors.md) - Error codes" in sub


def test_folders_without_markdown_are_not_part_of_the_tree(project):
    bundle = project / "context-db" / "demo-project"
    write(bundle / "images" / "diagram.svg", "<svg/>")
    write(bundle / "scripts" / "nested" / "tool.py", "print()\n")
    result = run(project, "index")
    assert result.returncode == 0, result.stdout
    assert not (bundle / "images" / "index.md").exists()
    assert not (bundle / "scripts" / "nested" / "index.md").exists()
    assert "images" not in (bundle / "index.md").read_text()


def test_a_folder_left_with_only_its_index_is_reported(project):
    bundle = project / "context-db" / "demo-project"
    write(bundle / "gone" / "gone.md", "---\ntype: Folder\ndescription: Soon empty\n---\n")
    assert run(project, "index").returncode == 0
    (bundle / "gone" / "gone.md").unlink()
    result = run(project, "index")
    assert result.returncode == 0
    assert "gone/: holds only an index.md" in result.stdout
    assert "gone" not in (bundle / "index.md").read_text()


def test_what_git_ignores_stays_out_of_the_index_and_the_checks(project, tmp_path):
    git(project, "init", "-q", "-b", "main")
    bundle = project / "context-db" / "demo-project"
    write(
        project / ".gitignore",
        "context-db/demo-project/private/\ncontext-db/demo-project/secret.md\n"
        "context-db/demo-project/mine\ncontext-db/notes\n",
    )
    write(bundle / "private" / "scratch.md", "no frontmatter at all\n")
    write(bundle / "secret.md", "no frontmatter either\n")
    (tmp_path / "elsewhere").mkdir(exist_ok=True)
    (bundle / "mine").symlink_to(tmp_path / "elsewhere")
    result = run(project, "index")
    assert result.returncode == 0, result.stdout
    index = (bundle / "index.md").read_text()
    assert "private" not in index and "secret" not in index
    assert not (bundle / "private" / "index.md").exists()
    assert run(project, "index", "--check").returncode == 0

    # A folder that is ignored as a whole is private, and is indexed as it stands.
    notes = project / "context-db" / "notes"
    write(notes / "notes.md", "---\ntype: Folder\ndescription: My notes\n---\n")
    write(notes / "idea.md", doc(description="An idea"))
    result = run(project, "index", "context-db/notes")
    assert result.returncode == 0, result.stdout
    assert "An idea" in (notes / "index.md").read_text()


def test_index_is_idempotent_and_check_detects_drift(project):
    assert "up to date" in run(project, "index").stdout
    assert run(project, "index", "--check").returncode == 0
    write(project / "context-db" / "demo-project" / "new.md", doc())
    result = run(project, "index", "--check")
    assert result.returncode == 1
    assert "out of date" in result.stdout
    assert "Fix them, then run:  python3 " in result.stdout and " index" in result.stdout
    assert "new.md" not in (project / "context-db" / "demo-project" / "index.md").read_text()


def test_index_refuses_to_write_through_a_symlink(example):
    for target in ("context-db/coding-standards", "context-db/git-standards/"):
        result = run(example, "index", target)
        assert result.returncode != 0
        assert "symlink" in result.stdout
    assert not (example / "context-db" / "coding-standards" / "stray.md").exists()


def test_index_accepts_an_explicit_folder_without_any_config(tmp_path):
    write(tmp_path / "shared" / "shared.md", "---\ntype: Folder\ndescription: Shared\n---\n")
    write(tmp_path / "shared" / "rule.md", doc())
    result = run(tmp_path, "index", "shared")
    assert result.returncode == 0, result.stdout
    assert (tmp_path / "shared" / "index.md").exists()


def test_index_on_a_subfolder_indexes_the_whole_bundle(project):
    bundle = project / "context-db" / "demo-project"
    write(bundle / "new.md", doc(description="Brand new"))
    result = run(project, "index", "context-db/demo-project/wip")
    assert result.returncode == 0, result.stdout
    assert "indexing all of context-db/demo-project/" in result.stdout
    assert "Brand new" in (bundle / "index.md").read_text()
    assert "okf_version" not in (bundle / "wip" / "index.md").read_text()


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
    result = run(project, "index")
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
    result = run(project, "index")
    assert result.returncode == 0, result.stdout


def test_symlink_inside_a_bundle_is_an_error(project, tmp_path):
    (tmp_path / "elsewhere").mkdir(exist_ok=True)
    (project / "context-db" / "demo-project" / "linked").symlink_to(tmp_path / "elsewhere")
    result = run(project, "index")
    assert result.returncode == 1
    assert "symlink inside a bundle" in result.stdout


def test_oversized_file_warns_but_wip_is_exempt(project):
    bundle = project / "context-db" / "demo-project"
    long_body = "# T\n\n" + "line\n" * 250
    write(bundle / "big.md", doc(body=long_body))
    write(bundle / "wip" / "plan.md", doc("Plan", body=long_body))
    result = run(project, "index")
    assert result.returncode == 0
    assert "WARNING" in result.stdout and "big.md" in result.stdout
    assert "plan.md:" not in result.stdout


# ── Things every command shares ──────────────────────────────────────────────


def test_version_and_help():
    assert run(REPO, "--version").stdout.strip() == "context-db 0.1 (OKF 0.2)"
    for args in ((), ("help",)):
        out = run(REPO, *args).stdout
        assert "prompt" in out and "configure" in out


def test_commands_without_config_ask_for_configure(tmp_path):
    (tmp_path / "context-db").mkdir()
    for command in ("prompt", "update", "wip"):
        result = run(tmp_path, command, "anything")
        assert result.returncode == 0
        assert "/context-db configure" in result.stdout


def test_broken_config_is_reported_cleanly(project):
    config = project / "context-db" / "context-db.json"
    config.write_text("{not json")
    result = run(project, "prompt", "x")
    assert result.returncode != 0
    assert "is not valid JSON" in result.stdout and "Traceback" not in result.stdout
    config.write_text('{"project": "demo"}')
    result = run(project, "prompt", "x")
    assert result.returncode != 0
    assert "has no python, main_branch, update_mode" in result.stdout


def test_no_placeholder_is_left_unfilled(example):
    for args in (
        ("prompt", "x"),
        ("update",),
        ("update", "x", "--push"),
        ("wip", "x"),
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
    for args in (("prompt", "x"), ("update",), ("wip",), ("configure",), ("index",)):
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
    assert "start at `context-db/git-standards/index.md`" in out
    assert "wip/refund-endpoint.md` — Adding POST /refunds" in out
    assert "[branch: feature/refunds]" in out
    assert "context-db-on-markdown" not in out.split("# Folders")[1]
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


def test_prompt_handles_unindexed_and_broken_mounts(project):
    cdb = project / "context-db"
    write(cdb / "legacy" / "legacy.md", "---\ndescription: Old format folder\n---\n")
    (cdb / "dangling").symlink_to(project / "does-not-exist")
    out = run(project, "prompt", "x").stdout
    assert "`context-db/legacy/` (it has no `index.md`" in out
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
    assert "context-db.py index" in out
    assert "# Commit" not in out
    assert "# User Instruction" not in out


def test_update_commit_and_push(project):
    commit = run(project, "update", "note this", "--commit").stdout
    assert "go straight to the Commit section" in commit
    assert commit.index("# Commit") < commit.index("# User Instruction")
    assert "Do not push." in commit
    assert commit.rstrip().endswith("note this")
    assert "Then push the current branch" in run(project, "update", "--push").stdout


def test_on_file_is_inlined_without_comments_or_frontmatter(project):
    write(
        project / "context-db" / "context-db-on-markdown" / "ON_UPDATE.md",
        "---\ndescription: ignored\n---\n<!-- hidden\nnote -->\nAlways cite the ticket.\n",
    )
    out = run(project, "update", "--commit").stdout
    assert "Always cite the ticket." in out
    assert out.index("# Commit") < out.index("Always cite the ticket.")
    assert "hidden" not in out and "ignored" not in out


def test_on_rules_keep_a_heading_the_author_wrote(project):
    on_file = project / "context-db" / "context-db-on-markdown" / "ON_PROMPT.md"
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
    assert run(project, "init", "--local", "python=/opt/py/bin/python3").returncode == 0
    assert "/opt/py/bin/python3 " in run(project, "update").stdout
    assert "/opt/py/bin/python3 " in run(project, "wip").stdout
    assert "/opt/py/bin/python3 " in run(project, "configure").stdout
    shared = json.loads((project / "context-db" / "context-db.json").read_text())
    assert shared["python"] == "python3"


# ── wip ──────────────────────────────────────────────────────────────────────


def test_wip_shows_git_state_and_every_wip_file(project):
    git(project, "init", "-q", "-b", "main")
    git(project, "add", "-A")
    git(project, "commit", "-q", "-m", "base")
    git(project, "checkout", "-q", "-b", "feature/x")
    write(project / "src.py", "print('hi')\n")
    git(project, "add", "-A")
    git(project, "commit", "-q", "-m", "add src")
    write(project / "context-db" / "demo-project" / "wip" / "x-plan.md", doc("Plan", "The X plan"))
    out = run(project, "wip", "plan the x work").stdout
    assert "- Current branch: `feature/x`" in out
    assert "- Main branch: `main`" in out
    assert "Work has landed when it is merged into `main`" in out
    assert "add src" in out
    assert "src.py" in out
    assert "x-plan.md" in out.split("git status --short")[1]
    assert "wip/x-plan.md` — The X plan" in out
    assert "`branch: feature/x`" in out
    assert out.rstrip().endswith("plan the x work")


def test_wip_on_the_main_branch_shows_recent_commits(project):
    git(project, "init", "-q", "-b", "main")
    git(project, "add", "-A")
    git(project, "commit", "-q", "-m", "only commit")
    out = run(project, "wip").stdout
    assert "## Recent commits" in out and "only commit" in out


def test_wip_says_so_when_the_main_branch_does_not_exist(project):
    git(project, "init", "-q", "-b", "trunk")
    git(project, "add", "-A")
    git(project, "commit", "-q", "-m", "base")
    out = run(project, "wip").stdout
    assert "main branch `main` does not exist" in out
    assert "base" in out


def test_wip_outside_git(project):
    out = run(project, "wip").stdout
    assert "Not a git repository" in out
    assert "holds no plans" in out


# ── configure and init ───────────────────────────────────────────────────────


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


def test_an_empty_folder_gets_an_index_that_says_so(project):
    wip_index = project / "context-db" / "demo-project" / "wip" / "index.md"
    assert wip_index.read_text() == "<!-- Nothing is in this folder yet. -->\n"


def test_configure_reports_state_and_v0_leftovers(tmp_path):
    write(tmp_path / "context-db" / "ON_PROMPT.md", "old\n")
    write(tmp_path / "context-db" / "acme-project" / "wip.md", "old\n")
    out = run(tmp_path, "configure").stdout
    assert "context-db.json`: does not exist" in out
    assert "`context-db/acme-project/`" in out
    assert "Suggested project name: `acme` (from the existing project folder)" in out
    assert "v0.0 layout" in out and "ON_PROMPT.md" in out and "wip.md" in out
    assert " init --project <name>" in out


def test_configure_still_runs_when_the_config_is_broken(project):
    config = project / "context-db" / "context-db.json"
    for broken in ("{not json", '{"project": "demo"}', "[]"):
        config.write_text(broken)
        result = run(project, "configure")
        assert result.returncode == 0, result.stdout
        assert "# Detected State" in result.stdout
    config.write_text("{not json")
    assert "is not valid JSON" in run(project, "configure").stdout


def test_init_scaffolds_and_never_overwrites(tmp_path):
    subprocess.run(["git", "init", "-q"], cwd=str(tmp_path), check=True)
    result = run(
        tmp_path, "init", "--main-branch", "trunk", "--python", "python3.11", "--project", "demo"
    )
    assert result.returncode == 0, result.stdout
    cdb = tmp_path / "context-db"
    assert (cdb / "context-db.json").read_text() == (
        '{\n  "project": "demo",\n  "python": "python3.11",\n  "main_branch": "trunk",\n'
        '  "update_mode": "on-command"\n}\n'
    )
    for name in ("ON_PROMPT.md", "ON_UPDATE.md", "ON_WIP.md", "ON_CONFIGURE.md"):
        assert (cdb / "context-db-on-markdown" / name).exists()
    assert (cdb / "demo-project" / "demo-project.md").exists()
    assert (cdb / "demo-project" / "wip" / "wip.md").exists()
    assert "context-db/context-db.local.json" in (tmp_path / ".gitignore").read_text()

    write(cdb / "context-db-on-markdown" / "ON_PROMPT.md", "mine\n")
    again = run(tmp_path, "init", "--main-branch", "main")
    assert again.returncode == 0
    kept = (cdb / "context-db-on-markdown" / "ON_PROMPT.md").read_text()
    assert kept.startswith("mine\n") and "context-db update mode" in kept
    config = json.loads((cdb / "context-db.json").read_text())
    assert config["main_branch"] == "main" and config["python"] == "python3.11"
    assert (tmp_path / ".gitignore").read_text().count("context-db.local.json") == 1


def test_update_mode_is_written_into_on_prompt_and_reaches_the_agent(tmp_path):
    assert run(tmp_path, "init", "--project", "demo").returncode == 0
    on_prompt = tmp_path / "context-db" / "context-db-on-markdown" / "ON_PROMPT.md"
    out = run(tmp_path, "prompt", "x").stdout
    assert "only when the user runs `/context-db update`" in out
    assert "<!--" not in out

    result = run(tmp_path, "init", "--update-mode", "agent-decides")
    assert result.returncode == 0, result.stdout
    out = run(tmp_path, "prompt", "x").stdout
    assert "You may update the knowledge base without being asked" in out
    assert "context-db.py update '<what you learned>'" in out
    assert "only when the user runs" not in out
    config = json.loads((tmp_path / "context-db" / "context-db.json").read_text())
    assert config["update_mode"] == "agent-decides"

    # The user may reword the paragraph; a later init without the flag keeps it.
    on_prompt.write_text(on_prompt.read_text().replace("Keep the bar high", "Be picky"))
    assert run(tmp_path, "init").returncode == 0
    assert "Be picky" in on_prompt.read_text()
    assert on_prompt.read_text().count("context-db update mode: written") == 1
    assert run(tmp_path, "init", "--update-mode", "sometimes").returncode != 0


def test_configure_asks_its_questions_as_a_menu(tmp_path):
    out = run(tmp_path, "configure").stdout
    assert "AskUserQuestion" in out
    assert "`on-command`" in out and "`agent-decides`" in out
    assert "--update-mode <mode>" in out


def test_init_rejects_bad_input_without_writing_anything(tmp_path):
    for args in (
        (),
        ("--project", "has space"),
        ("--project", "a/b"),
        ("--project", "demo", "--local", "colour=blue"),
        ("--project", "demo", "--local", "python"),
    ):
        assert run(tmp_path, "init", *args).returncode != 0
    assert not (tmp_path / "context-db").exists()


def test_init_catches_a_project_name_given_with_its_suffix(tmp_path):
    write(tmp_path / "context-db" / "acme-project" / "acme-project.md", doc("Folder", "Acme"))
    result = run(tmp_path, "init", "--project", "acme-project")
    assert result.returncode != 0
    assert "--project acme" in result.stdout
    assert not (tmp_path / "context-db" / "acme-project-project").exists()


# ── The shipped trees stay clean ─────────────────────────────────────────────


def test_example_project_and_shared_folders_are_conformant(example):
    assert run(example, "index", "--check").returncode == 0
    shared = example.parent / "shared"
    for name in ("coding-standards", "git-standards"):
        result = run(shared, "index", name, "--check")
        assert result.returncode == 0, result.stdout


def test_this_repos_own_knowledge_base_is_conformant():
    result = run(REPO, "index", "--check")
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
        if path.name == "index.md":
            if content.startswith("---"):
                header = content.split("---")[1]
                assert yaml.safe_load(header) == {"okf_version": "0.2"}, path
            continue
        assert content.startswith("---\n"), path
        expected = yaml.safe_load(content.split("\n---", 1)[0][4:])
        meta, _ = context_db.parse_frontmatter(content)
        assert isinstance(expected["type"], str) and expected["type"], path
        for key in ("type", "description", "status", "branch"):
            if key in expected:
                assert meta[key] == " ".join(str(expected[key]).split()), (path, key)


def test_index_files_follow_the_okf_shape():
    """OKF section 8: headings, then `* [Title](url) - description` entries."""
    entry = re.compile(r"^\* \[.+\]\([^)\s]+\)( - .+)?$")
    for path in shipped_documents():
        if path.name != "index.md":
            continue
        body = path.read_text(encoding="utf-8")
        if body.startswith("---"):
            body = body.split("---", 2)[2]
        allowed = ("# Subfolders", "# Files", "<!-- Nothing is in this folder yet. -->")
        for line in body.splitlines():
            assert not line or line in allowed or entry.match(line), (path, line)


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
    assert (cdb / "context-db-on-markdown" / "ON_PROMPT.md").exists()
    plan = (bundle / "wip" / "current-work.md").read_text()
    assert plan.startswith("---\ntype: Plan\n")
    assert "[standards.md](../standards.md)" in plan
    assert (bundle / "wip" / "wip.md").read_text().startswith("---\ntype: Folder\n")
    assert "Follows [standards.md](../standards.md)." in (bundle / "api" / "errors.md").read_text()
    mentions = result.stdout.split("Mentions of v0.0 machinery")[1]
    assert "api/errors.md:6: `TOC script`" in mentions
    decide = result.stdout.split("Needs a decision")[1].split("## Mentions")[0]
    assert "ON_MAINTAIN.md" in decide
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
    init = run(tmp_path, "init", "--project", "acme")
    assert init.returncode == 0, init.stdout
    assert "Be careful." in run(tmp_path, "prompt", "x").stdout
    assert (bundle / "index.md").exists()
