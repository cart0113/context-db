"""Tests for skill/context-db/context-db.py and the v0.0 migration script.

Every test runs the real script as a subprocess inside a throwaway project, the
way an agent would.
"""

import importlib.util
import json
import os
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

spec = importlib.util.spec_from_file_location("context_db", SCRIPT)
context_db = importlib.util.module_from_spec(spec)
spec.loader.exec_module(context_db)


def run(cwd, *args, script=SCRIPT):
    return subprocess.run(
        [sys.executable, str(script), *args],
        check=False,
        cwd=str(cwd),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def doc(type_name="Reference", description="A thing", extra="", body="# Title\n\nBody.\n"):
    return f"---\ntype: {type_name}\ndescription: {description}\n{extra}---\n\n{body}"


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


@pytest.mark.parametrize("text", ["# No frontmatter\n", "---\ntype: X\nnever closed\n", ""])
def test_missing_frontmatter_is_none(text):
    meta, body = context_db.parse_frontmatter(text)
    assert meta is None
    assert body == text


def test_nested_keys_do_not_become_top_level():
    meta, _ = context_db.parse_frontmatter(
        "---\ntype: X\ngenerated:\n  by: someone\n  at: now\ndescription: d\n---\n"
    )
    assert "by" not in meta
    assert meta["description"] == "d"


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
    run(project, "index")
    index = (bundle / "index.md").read_text()
    assert "* [From Frontmatter](a.md)" in index
    assert "* [From Heading](b.md)" in index
    assert "* [c](c.md)" in index


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


def test_index_is_idempotent_and_check_detects_drift(project):
    assert "up to date" in run(project, "index").stdout
    assert run(project, "index", "--check").returncode == 0
    write(project / "context-db" / "demo-project" / "new.md", doc())
    result = run(project, "index", "--check")
    assert result.returncode == 1
    assert "out of date" in result.stdout
    assert "new.md" not in (project / "context-db" / "demo-project" / "index.md").read_text()


def test_index_refuses_a_symlinked_bundle(example):
    result = run(example, "index", "context-db/coding-standards")
    assert result.returncode != 0
    assert "symlink" in result.stdout


def test_index_accepts_an_explicit_bundle_without_any_config(tmp_path):
    write(tmp_path / "shared" / "shared.md", "---\ntype: Folder\ndescription: Shared\n---\n")
    write(tmp_path / "shared" / "rule.md", doc())
    result = run(tmp_path, "index", "shared")
    assert result.returncode == 0, result.stdout
    assert (tmp_path / "shared" / "index.md").exists()


# ── Lint ─────────────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "name, text, message",
    [
        ("x.md", "# No frontmatter\n", "no YAML frontmatter"),
        ("x.md", "---\ndescription: d\n---\n", "no `type`"),
        ("x.md", "---\ntype: X\n---\n", "no `description`"),
        ("x.md", doc(extra="status: experiment\n"), "status `experiment`"),
        ("x.md", doc(body="See [gone](./gone.md).\n"), "broken link `./gone.md`"),
        ("x.md", doc(body="See [root](/x.md).\n"), "root-relative"),
        ("sub/x.md", doc(), "no folder descriptor"),
    ],
)
def test_lint_errors(project, name, text, message):
    write(project / "context-db" / "demo-project" / name, text)
    result = run(project, "index")
    assert result.returncode == 1
    assert message in result.stdout


def test_lint_ignores_links_in_code_and_external_links(project):
    body = (
        "`[a](./gone.md)` and [site](https://example.com) and [anchor](#here) and\n"
        "[self](./retry-policy.md#section)\n\n```\n[b](./gone.md)\n```\n"
    )
    write(project / "context-db" / "demo-project" / "x.md", doc(body=body))
    assert run(project, "index").returncode == 0


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


# ── prompt ───────────────────────────────────────────────────────────────────


def test_commands_without_config_ask_for_configure(tmp_path):
    (tmp_path / "context-db").mkdir()
    for command in ("prompt", "update", "wip"):
        result = run(tmp_path, command, "anything")
        assert result.returncode == 0
        assert "/context-db configure" in result.stdout


def test_prompt_without_instruction(project):
    assert "Ask the user" in run(project, "prompt").stdout


def test_prompt_lists_bundles_wip_and_ends_with_rules_then_instruction(example):
    out = run(example, "prompt", "add a refund endpoint").stdout
    assert "**Project bundle** `context-db/acme-payments-project/`" in out
    assert "**Background bundle** `context-db/coding-standards/`" in out
    assert "start at `context-db/git-standards/index.md`" in out
    assert "wip/refund-endpoint.md` — Adding POST /refunds" in out
    assert "[branch: feature/refunds]" in out
    assert "context-db-on-markdown" not in out.split("# Bundles")[1]
    order = [
        out.index(s)
        for s in ("# Bundles", "# Work In Progress", "PCI-scoped", "# User Instruction")
    ]
    assert order == sorted(order)
    assert out.rstrip().endswith("add a refund endpoint")
    assert "<!--" not in out


def test_prompt_handles_unindexed_and_broken_mounts(project):
    cdb = project / "context-db"
    write(cdb / "legacy" / "legacy.md", "---\ndescription: Old format bundle\n---\n")
    (cdb / "dangling").symlink_to(project / "does-not-exist")
    out = run(project, "prompt", "x").stdout
    assert "`context-db/legacy/` (it has no `index.md`" in out
    assert "Old format bundle" in out
    assert "`context-db/dangling/` is a broken symlink" in out


def test_mounted_bundle_descriptor_is_found_under_its_real_name(project, tmp_path):
    source = tmp_path / "elsewhere" / "coding-standards"
    write(source / "coding-standards.md", "---\ntype: Folder\ndescription: Real name wins\n---\n")
    (project / "context-db" / "general-standards").symlink_to(source)
    assert "Real name wins" in run(project, "prompt", "x").stdout


def test_paths_are_relative_to_the_callers_cwd(project):
    subprocess.run(["git", "init", "-q"], cwd=str(project), check=True)
    sub = project / "src"
    sub.mkdir()
    out = run(sub, "prompt", "x").stdout
    assert "`../context-db/demo-project/`" in out


# ── update ───────────────────────────────────────────────────────────────────


def test_update_puts_the_gate_before_the_mechanics(project):
    out = run(project, "update").stdout
    assert (
        out.index("nothing to add and stop")
        < out.index("## Where it goes")
        < out.index("# File Format")
    )
    assert "context-db.py index" in out
    assert "# Commit" not in out
    assert "# User Instruction" not in out


def test_update_commit_and_push(project):
    commit = run(project, "update", "note this", "--commit").stdout
    assert "go straight to the Commit section" in commit
    assert commit.index("# User Instruction") < commit.index("# Commit")
    assert "Do not push." in commit
    assert "Then push the current branch" in run(project, "update", "--push").stdout


def test_on_file_is_inlined_without_comments_or_frontmatter(project):
    write(
        project / "context-db" / "context-db-on-markdown" / "ON_UPDATE.md",
        "---\ndescription: ignored\n---\n<!-- hidden\nnote -->\nAlways cite the ticket.\n",
    )
    out = run(project, "update").stdout
    assert "Always cite the ticket." in out
    assert "hidden" not in out and "ignored" not in out


def test_printed_commands_use_the_local_interpreter_override(project):
    assert run(project, "init", "--local", "python=/opt/py/bin/python3").returncode == 0
    assert "/opt/py/bin/python3 " in run(project, "update").stdout
    shared = json.loads((project / "context-db" / "context-db.json").read_text())
    assert shared["python"] == "python3"


# ── wip ──────────────────────────────────────────────────────────────────────


def git(cwd, *args):
    subprocess.run(
        ["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *args],
        cwd=str(cwd),
        check=True,
        stdout=subprocess.DEVNULL,
    )


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
    assert "add src" in out
    assert "src.py" in out
    assert "x-plan.md" in out.split("git status --short")[1]
    assert "wip/x-plan.md` — The X plan" in out
    assert "`branch: feature/x`" in out
    assert out.rstrip().endswith("plan the x work")


def test_wip_outside_git(project):
    env_dir = project
    out = run(env_dir, "wip").stdout
    assert "# Git State" in out
    assert "is empty" in out


# ── configure and init ───────────────────────────────────────────────────────


def test_configure_reports_state_and_v0_leftovers(tmp_path):
    write(tmp_path / "context-db" / "ON_PROMPT.md", "old\n")
    write(tmp_path / "context-db" / "acme-project" / "wip.md", "old\n")
    out = run(tmp_path, "configure").stdout
    assert "context-db.json`: does not exist" in out
    assert "`context-db/acme-project/`" in out
    assert "v0.0 layout" in out and "ON_PROMPT.md" in out and "wip.md" in out
    assert " init --project <name>" in out


def test_init_scaffolds_and_never_overwrites(tmp_path):
    subprocess.run(["git", "init", "-q"], cwd=str(tmp_path), check=True)
    result = run(
        tmp_path, "init", "--project", "demo", "--python", "python3.11", "--main-branch", "trunk"
    )
    assert result.returncode == 0, result.stdout
    cdb = tmp_path / "context-db"
    assert json.loads((cdb / "context-db.json").read_text()) == {
        "project": "demo",
        "python": "python3.11",
        "main_branch": "trunk",
    }
    for name in ("ON_PROMPT.md", "ON_UPDATE.md", "ON_WIP.md", "ON_CONFIGURE.md"):
        assert (cdb / "context-db-on-markdown" / name).exists()
    assert (cdb / "demo-project" / "demo-project.md").exists()
    assert (cdb / "demo-project" / "wip" / "wip.md").exists()
    assert "context-db/context-db.local.json" in (tmp_path / ".gitignore").read_text()

    write(cdb / "context-db-on-markdown" / "ON_PROMPT.md", "mine\n")
    again = run(tmp_path, "init", "--main-branch", "main")
    assert again.returncode == 0
    assert (cdb / "context-db-on-markdown" / "ON_PROMPT.md").read_text() == "mine\n"
    config = json.loads((cdb / "context-db.json").read_text())
    assert config["main_branch"] == "main" and config["python"] == "python3.11"
    assert (tmp_path / ".gitignore").read_text().count("context-db.local.json") == 1


def test_init_needs_a_project_name_and_rejects_unknown_local_keys(tmp_path):
    assert run(tmp_path, "init").returncode != 0
    assert run(tmp_path, "init", "--project", "demo", "--local", "colour=blue").returncode != 0


# ── The shipped trees stay clean ─────────────────────────────────────────────


def test_example_project_and_shared_bundles_are_conformant(example):
    assert run(example, "index", "--check").returncode == 0
    shared = example.parent / "shared"
    for name in ("coding-standards", "git-standards"):
        result = run(shared, "index", name, "--check")
        assert result.returncode == 0, result.stdout


def test_this_repos_own_bundle_is_conformant():
    result = run(REPO, "index", "--check")
    assert result.returncode == 0, result.stdout


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
        "# Decisions\n\nSee `./standards.md` and `./missing.md`.\n\n```\n`./standards.md`\n```\n",
    )
    write(bundle / "standards.md", "---\ndescription: Coding standards\n---\n\n# Standards\n")

    dry = run(tmp_path, "context-db", "--dry-run", script=MIGRATE)
    assert dry.returncode == 0 and (cdb / "ON_PROMPT.md").exists()

    result = run(tmp_path, "context-db", script=MIGRATE)
    assert result.returncode == 0, result.stdout
    assert (cdb / "context-db-on-markdown" / "ON_PROMPT.md").exists()
    assert (bundle / "wip" / "current-work.md").exists()
    assert "[standards.md](../standards.md)" in (bundle / "wip" / "current-work.md").read_text()
    assert "ON_MAINTAIN.md" in result.stdout.split("Needs a decision")[1]
    assert "`./missing.md` does not resolve" in result.stdout

    decisions = (bundle / "design-decisions.md").read_text()
    assert decisions.startswith("---\ntype: Decision\n")
    assert "status: draft" in decisions
    assert "[standards.md](./standards.md)" in decisions
    assert "```\n`./standards.md`\n```" in decisions
    assert (bundle / "acme-project.md").read_text().startswith("---\ntype: Folder\n")
    assert (bundle / "standards.md").read_text().startswith("---\ntype: Convention\n")

    init = run(tmp_path, "init", "--project", "acme")
    assert init.returncode == 0, init.stdout
    assert "Be careful." in run(tmp_path, "prompt", "x").stdout
    assert os.path.exists(str(bundle / "index.md"))
