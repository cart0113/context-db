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
    # At the top of the knowledge base a mount is listed, and the settings folder is not.
    top = toc(example, "context-db")
    assert "* [coding-standards](context-db/coding-standards/) - Shared coding standards" in top
    assert "configuration" not in top


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


def test_an_index_file_in_the_project_folder_is_accepted_and_kept_honest(project):
    """Standard OKF: a project may keep index.md files. `toc` still lists from the files."""
    bundle = project / "context-db" / "demo-project"
    index = "# Files\n\n* [Retry](retry-policy.md) - Retry with backoff\n* [Wip](wip/) - Plans\n"
    write(bundle / "index.md", index)
    result = run(project, "toc", "--check")
    assert result.returncode == 0, result.stdout
    assert "WARNING" not in result.stdout
    listing = toc(project)
    assert "Read from its files just now." in listing
    assert "(context-db/demo-project/index.md)" not in listing  # never an entry of its own
    # The agent hears about the index only where there is one, and there it must keep it up.
    assert (
        "This folder also keeps an index file, `context-db/demo-project/index.md`, for people"
        in listing
    )
    assert "change its line in that file to match" in listing
    assert "index file" not in toc(project, "context-db/demo-project/wip")

    write(bundle / "new.md", doc(description="Just added"))
    write(bundle / "deep" / "deep.md", doc("Folder", "A subfolder", body=""))
    write(bundle / "deep" / "note.md", doc())
    write(bundle / "index.md", index + "* [Gone](gone.md) - Long since deleted\n")
    result = run(project, "toc", "--check")
    assert result.returncode == 0, result.stdout  # out of step is a warning, not an error
    assert "demo-project/index.md: does not list `new.md`, `deep/` — add a line" in result.stdout
    assert "index.md: lists `context-db/demo-project/gone.md`, which is not there" in result.stdout
    listing = toc(project)
    assert "Just added" in listing and "Long since deleted" not in listing


# ── A folder that comes with its own index.md ────────────────────────────────


def catalog(folder, entries=("Orders", "Refunds")):
    """A folder of notes the way a plain OKF tool leaves it: an index.md, no descriptor."""
    lines = [f"* [{name}]({name.lower()}.md) - All about {name.lower()}" for name in entries]
    write(folder / "index.md", '---\nokf_version: "0.2"\n---\n\n# Tables\n\n' + "\n".join(lines))
    for name in entries:
        write(folder / f"{name.lower()}.md", doc(description=f"Read from {name.lower()}.md"))


def test_a_folder_that_comes_with_an_index_is_listed_from_it(project):
    shared = project / "context-db" / "catalog"
    catalog(shared)
    index = shared / "index.md"
    index.write_text(
        index.read_text()
        + "\n* [Billing](./billing/) - Invoices and rates\n"
        + "* [Spec](https://example.com/spec#tables) - Kept elsewhere\n\n"
        + "Back to [the top](#tables).\n"
    )
    write(shared / "billing" / "rates.md", doc(description="Rate tables"))
    listing = toc(project, "context-db/catalog")
    assert listing.startswith(
        "# Contents of `context-db/catalog/`\n\nRead from `context-db/catalog/index.md`, the index"
    )
    assert "context-db.py toc <path>" in listing
    assert "* [Orders](context-db/catalog/orders.md) - All about orders" in listing
    assert "* [Billing](context-db/catalog/billing/) - Invoices and rates" in listing
    assert "(https://example.com/spec#tables)" in listing and "[the top](#tables)" in listing
    assert "okf_version" not in listing and "Read from orders.md" not in listing
    sub = toc(project, "context-db/catalog/billing")  # no index of its own, so it is built
    assert "Read from its files just now." in sub
    assert "* [Title](context-db/catalog/billing/rates.md) - Rate tables" in sub


def test_an_index_that_lists_nothing_is_not_used(project):
    shared = project / "context-db" / "catalog"
    catalog(shared)
    (shared / "index.md").write_text('---\nokf_version: "0.2"\n---\n')
    listing = toc(project, "context-db/catalog")
    assert "Read from its files just now." in listing
    assert "* [Title](context-db/catalog/orders.md) - Read from orders.md" in listing


def test_a_folder_with_only_an_index_is_described_by_what_it_lists(project):
    cdb = project / "context-db"
    catalog(cdb / "catalog")
    catalog(cdb / "big", entries=[f"Table{n}" for n in range(11)])
    catalog(cdb / "described")
    write(
        cdb / "described" / "described.md", "---\ntype: Folder\ndescription: Said outright\n---\n"
    )
    folders = run(project, "prompt", "x").stdout.split("# Folders")[1]
    assert (
        "**Background folder** `context-db/catalog/`: "
        "(no description; it holds Orders, Refunds)" in folders
    )
    assert "it holds Table0, Table1" in folders and "Table7, and 3 more)" in folders
    assert "**Background folder** `context-db/described/`: Said outright" in folders
    assert "Read from `context-db/described/index.md`" in toc(project, "context-db/described")


def test_an_index_stands_in_for_a_descriptor_only_in_a_folder_from_elsewhere(project):
    cdb = project / "context-db"
    catalog(cdb / "catalog")
    result = run(project, "toc", "context-db/catalog", "--check")
    assert result.returncode == 0, result.stdout  # its index is fine and stands in for a descriptor
    assert "WARNING" not in result.stdout  # and nobody here keeps that index in step
    write(cdb / "catalog" / "bare" / "note.md", doc())
    result = run(project, "toc", "context-db/catalog", "--check")
    assert result.returncode == 1 and "bare/: no folder descriptor" in result.stdout

    write(cdb / "demo-project" / "index.md", "# Files\n\n* [Gone](gone.md) - Long since deleted\n")
    assert "Long since deleted" not in toc(project)  # the project folder is listed from its files
    assert "Read from its files just now." in toc(project)
    write(cdb / "demo-project" / "sub" / "index.md", "* [Note](note.md) - A note\n")
    write(cdb / "demo-project" / "sub" / "note.md", doc())
    result = run(project, "toc", "--check")
    assert result.returncode == 1 and "sub/: no folder descriptor" in result.stdout


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


def test_a_description_that_runs_long_warns(project):
    """The description is read far more often than the file, so it has a size of its own."""
    bundle = project / "context-db" / "demo-project"
    write(bundle / "ok.md", doc(description="word " * 60))
    write(bundle / "many-topics.md", doc(description="word " * 70))
    write(bundle / "sub" / "sub.md", doc("Folder", "word " * 70, body=""))
    write(bundle / "sub" / "note.md", doc())
    result = run(project, "toc", "--check")
    assert result.returncode == 0, result.stdout
    assert "ok.md" not in result.stdout
    assert (
        "many-topics.md: description is 349 characters — say what the file holds" in result.stdout
    )
    assert "the file holds several topics and should be split (max 300)" in result.stdout
    assert "sub/sub.md: description is 349 characters — say what kind of thing" in result.stdout


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


USER_COMMANDS = ("prompt", "update", "wip", "maintain", "configure")


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


SHOWN = re.compile(
    r"(?s)\A(# context-db Show Context\n.*?)\n======== start of the message ========\n"
    r"(.*)\n======== end of the message ========\n\n(.*)\Z"
)


@pytest.mark.parametrize(
    "args",
    [
        ("prompt", "the task"),
        ("prompt", "the task", "--audit"),
        ("prompt",),
        ("update", "note this", "--push"),
        ("wip",),
        ("wip", "--list"),
        ("wip", "--maintain"),
        ("wip", "--clear"),
        ("configure",),
        ("maintain",),
    ],
)
def test_show_context_wraps_the_very_same_message_for_the_user_to_read(project, args):
    plain = run(project, *args).stdout
    before, message, after = SHOWN.match(run(project, *args, "--show-context").stdout).groups()
    assert message + "\n" == plain
    assert f"`--show-context` to `/context-db {args[0]}`" in before
    assert "word for word" in before and "Do not follow the message" in before
    assert "do nothing it says" in after


def test_show_context_also_covers_a_repository_that_is_not_set_up(tmp_path):
    (tmp_path / "context-db").mkdir()
    for command in ("prompt", "update", "wip", "maintain"):
        out = run(tmp_path, command, "x", "--show-context").stdout
        assert out.startswith("# context-db Show Context"), command
        assert "/context-db configure" in SHOWN.match(out).group(2)


def test_show_context_refuses_setting_flags_and_writes_nothing(tmp_path):
    result = run(tmp_path, "configure", "--project", "demo", "--show-context")
    assert result.returncode != 0
    assert "--show-context shows the message a command sends" in result.stdout
    assert not (tmp_path / "context-db").exists()
    assert run(tmp_path, "toc", "--show-context").returncode != 0  # toc has no such flag
    for command in USER_COMMANDS:
        assert "--show-context" in run(REPO, command, "--help").stdout


def flat(markdown):
    return " ".join(markdown.replace("`", "").split())


def test_help_readme_and_docs_home_describe_the_commands_alike():
    """The summaries in the script are one bullet list on both front pages, configure last."""
    assert USER_COMMANDS[-1] == "configure"  # the owner: "configure should always be listed last"
    assert tuple(context_db.COMMAND_SUMMARIES) == USER_COMMANDS
    summaries = {name: flat(context_db.COMMAND_SUMMARIES[name]) for name in USER_COMMANDS}
    for path in (REPO / "README.md", REPO / "docs" / "index.md"):
        page = path.read_text(encoding="utf-8")
        items = re.findall(
            r"(?ms)^- \[`/context-db (\w+)`\]\([^)]*#context-db-\1\):\n(.+?)(?=^- |\n\n)", page
        )
        assert {name: flat(text) for name, text in items} == summaries, path
        assert tuple(name for name, _ in items) == USER_COMMANDS, path
        assert "grid-item-card" not in page, path  # a plain list, not boxes
    # Python 3.8 puts a name as long as "configure" on a line of its own, with no space after it.
    listed = re.findall(r"(?m)^    (\w+)(?: |$)", run(REPO, "--help").stdout)
    assert tuple(listed) == USER_COMMANDS
    commands = (REPO / "docs" / "commands.md").read_text(encoding="utf-8")
    sections = tuple(re.findall(r"(?m)^## /context-db (\w+)$", commands))
    assert sections == USER_COMMANDS


def test_readme_and_docs_home_open_alike_and_briefly():
    """The owner's opening: the two kinds in one sentence, the Example, then a few plain lines."""
    openings = []
    for path in (REPO / "README.md", REPO / "docs" / "index.md"):
        opening = path.read_text(encoding="utf-8").split("## Benefits")[0]
        intro, rest = opening.split("## Example")
        two_kinds = rest.split("## Two kinds of knowledge")[1]
        said = flat(intro)
        assert "A set of skills for coding agents. context-db helps you manage" in said, path
        assert "It also provides a framework for managing usage information" in said, path
        assert "|" not in two_kinds, path  # the owner found a table here "weird"
        assert len(two_kinds.split()) < 160, path  # and twice this much "too detailed"
        assert "own knowledge still comes first" in flat(two_kinds), path
        openings.append(re.sub(r"\]\([^)]*\)", "]()", rest))  # only the links differ
    assert openings[0] == openings[1]


def sections_sent(output):
    """The top-level headings of a command's output, outside code blocks."""
    headings, fenced = [], False
    for line in output.split("\n"):
        if line.startswith("```"):
            fenced = not fenced
        elif line.startswith("# ") and not fenced:
            headings.append(line)
    return headings


EVERY_SECTION = {  # the flags that make each command send every section it can
    "prompt": ("--audit",),
    "update": ("--push",),
    "wip": (),
    "configure": (),
    "maintain": (),
}


def test_the_docs_list_the_sections_each_command_sends(example):
    """docs/commands.md, What each command sends: one table per command, in order."""
    page = (REPO / "docs" / "commands.md").read_text(encoding="utf-8")
    page = page.split("## What each command sends")[1]
    tables = re.findall(r"(?m)^`/context-db (\w+)` sends:\n\n((?:\|.*\n)+)", page)
    assert tuple(name for name, _ in tables) == USER_COMMANDS
    prompts = SCRIPT.parent / "prompts"
    for name, table in tables:
        rows = re.findall(r"(?m)^\| `(# [^`]+)` \| (.+) \|$", table)
        for on_file in (f"ON_{name.upper()}.md", f"ON_{name.upper()}.local.md"):
            write(example / "context-db" / "configuration" / on_file, "A rule.\n")
        out = run(example, name, "the task", *EVERY_SECTION[name]).stdout
        assert sections_sent(out) == [heading for heading, _ in rows], name
        for heading, source in rows:
            for prompt_file in re.findall(r"`prompts/([\w-]+\.md)`", source):
                first_line = (prompts / prompt_file).read_text(encoding="utf-8").split("\n")[0]
                assert first_line == heading, (name, prompt_file)
            for on_file in re.findall(r"`configuration/(ON_[\w.]+\.md)`", source):
                local = ".local" if heading == "# User Rules" else ""
                assert on_file == f"ON_{name.upper()}{local}.md"


def test_help_readme_and_docs_home_show_the_whole_api():
    """One block holds what the user types. --help prints it; the front pages repeat it."""
    api = context_db.API.strip("\n")
    assert api in run(REPO, "--help").stdout
    for path in (REPO / "README.md", REPO / "docs" / "index.md"):
        page = path.read_text(encoding="utf-8")
        assert f"```text\n{api}\n```" in page, path
        assert "Each command is a starting point." in page, path
        # The owner: "very inside baseball". The Commands page has them, as a workflow.
        assert "--commit" not in page and "--push" not in page, path
    typed = re.findall(r"(?m)^  /context-db (\w+)", api)
    assert set(typed) == set(USER_COMMANDS)
    for command in USER_COMMANDS:
        usage = run(REPO, command, "--help").stdout.split("\n\n")[0]
        flags = set(re.findall(r"--[\w-]+", usage))
        assert "--show-context" in flags, command
        if command != "configure":  # its setting flags are for the agent, and --help lists them
            flags -= {"--commit", "--push"}  # left out of the block on purpose
            assert all(flag in api for flag in flags), (command, flags)
    commands = (REPO / "docs" / "commands.md").read_text(encoding="utf-8")
    assert "## A command is a starting point" in commands


def test_prompt_update_and_maintain_take_no_flag_that_narrows_them(project):
    """Each covers the whole knowledge base. The user narrows it in words, in the instruction."""
    # --audit narrows nothing: prompt reads the same, and then reports what it read.
    allowed = {"prompt": {"--audit"}, "update": {"--commit", "--push"}, "maintain": set()}
    for command, flags in allowed.items():
        usage = run(REPO, command, "--help").stdout.split("\n\n")[0]
        assert set(re.findall(r"--[\w-]+", usage)) - {"--show-context"} == flags, command
        for gone in ("--wip", "--usage", "--use-git-diff", "--use-global-context"):
            result = run(project, command, "x", gone)
            assert result.returncode != 0 and "unrecognized arguments" in result.stdout, gone
    update = " ".join(run(project, "update", "only the usage folder").stdout.split())
    assert "If there is a user instruction at the end of this output, follow it." in update
    assert "It may say what to record, or narrow or widen where you look." in update
    maintain = " ".join(run(project, "maintain").stdout.split())
    assert "With a folder or a topic, look only there." in maintain


def test_sections_about_plans_and_usage_folders_are_sent_only_when_there_are_any(project):
    """docs/commands.md marks those rows "Only when"."""
    plans = ["# How to Check the Plans", "# Git State", "# Work In Progress"]
    usage = "# How to Check the Usage Folders"
    bare = sections_sent(run(project, "maintain").stdout)
    assert not set(plans + [usage]) & set(bare)
    assert "# Usage Knowledge" not in sections_sent(run(project, "update").stdout)
    add_plan(project)
    usage_folder(project / "context-db" / "demo-project" / "demo-usage")
    cut = bare.index("# Folders") + 1
    assert (
        sections_sent(run(project, "maintain").stdout) == bare[:cut] + plans + [usage] + bare[cut:]
    )
    sent = sections_sent(run(project, "update").stdout)
    assert sent[:2] == ["# context-db Update", "# Usage Knowledge"]
    page = (REPO / "docs" / "commands.md").read_text(encoding="utf-8")
    page = page.split("## What each command sends")[1]
    table = page.split("`/context-db maintain` sends:")[1]
    for heading in plans + [usage]:
        assert re.search(rf"(?m)^\| `{heading}` \| .*Only when .* \|$", table), heading
    assert re.search(r"(?m)^\| `# Usage Knowledge` \| .*Only when .* \|$", page)


def test_the_docs_show_a_real_prompt_message(example):
    """docs/examples/prompt-output.txt is what `prompt` prints in the example project.

    To refresh it, copy example/ somewhere outside a git repository, and there run
    `python3 .claude/skills/context-db/context-db.py prompt - > prompt-output.txt`
    with the instruction below on standard input.
    """
    snapshot = (REPO / "docs" / "examples" / "prompt-output.txt").read_text(encoding="utf-8")
    instruction = snapshot.split("# User Instruction\n\n")[1]
    result = subprocess.run(
        [sys.executable, ".claude/skills/context-db/context-db.py", "prompt", "-"],
        check=True,
        cwd=str(example),
        input=instruction,
        env=dict(os.environ, GIT_CEILING_DIRECTORIES=str(example.parent.parent)),
        stdout=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )
    assert result.stdout == snapshot
    page = (REPO / "docs" / "commands.md").read_text(encoding="utf-8")
    shown = page.split("## /context-db prompt")[1].split("```text\n/context-db prompt\n\n")[1]
    assert shown.split("```")[0] == instruction


def test_the_docs_show_every_instruction_file_and_name_every_setting_and_size():
    """Nothing the agent is told is hidden, and the numbers in the docs are the script's."""
    commands = (REPO / "docs" / "commands.md").read_text(encoding="utf-8")
    for prompt_file in sorted((SCRIPT.parent / "prompts").glob("*.md")):
        included = f"```{{literalinclude}} ../skill/context-db/prompts/{prompt_file.name}\n"
        assert commands.count(included) == 1, prompt_file.name
    setup = (REPO / "docs" / "setup.md").read_text(encoding="utf-8")
    for key in context_db.SETTINGS_KEYS + (context_db.SETTINGS_FILES,):
        assert f"`{key}`" in setup, key
    layout = flat((REPO / "docs" / "layout.md").read_text(encoding="utf-8"))
    assert f"a file over {context_db.MAX_FILE_LINES} lines outside wip/" in layout
    assert f"a description over {context_db.MAX_DESCRIPTION_CHARS} characters" in layout
    assert f"a folder with more than {context_db.MAX_FOLDER_ITEMS} items" in layout
    assert f"when a description passes {context_db.MAX_DESCRIPTION_CHARS} characters" in layout


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


def test_no_placeholder_is_left_unfilled(example, project):
    for args in (
        ("prompt", "x"),
        ("prompt", "x", "--audit"),
        ("audit",),
        ("prompt", "x", "--show-context"),
        ("update",),
        ("update", "x", "--push"),
        ("wip", "x"),
        ("wip", "--list"),
        ("wip", "--maintain"),
        ("wip", "--clear"),
        ("maintain",),
        ("maintain", "data-model"),
        ("configure",),
    ):
        out = run(example, *args).stdout
        assert not re.findall(r"\{[a-z_]+\}", out), args
        if args[0] in ("update", "maintain"):  # and in a project with no usage folder or plan
            assert not re.findall(r"\{[a-z_]+\}", run(project, *args).stdout), args


def test_an_unquoted_instruction_is_joined(project):
    out = run(project, "prompt", "add", "a", "refund", "endpoint").stdout
    assert out.rstrip().endswith("# User Instruction\n\nadd a refund endpoint")
    out = run(project, "update", "note", "this", "--push").stdout
    assert out.rstrip().endswith("note this")


def test_output_survives_an_ascii_only_stdout(project):
    env = dict(os.environ, PYTHONIOENCODING="ascii", PYTHONUTF8="0")
    for args in (("prompt", "x"), ("update",), ("wip",), ("wip", "--maintain"), ("configure",)):
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
    assert "**Usage folder** `context-db/acme-payments-project/acme-payments-usage/`: How" in out
    assert "**Background folder** `context-db/coding-standards/`" in out
    assert "**Background folder** `context-db/git-standards/`:" in out
    wip = out.split("# Work In Progress")[1].split("# Folders")[0]
    assert "relative to\n`context-db/acme-payments-project/wip/`" in wip
    assert "- [Refund endpoint](refund-endpoint.md). Started 2026-11-03" in wip
    assert "configuration" not in out.split("# Folders")[1].split("\n# ")[0]
    # The ledger keeps its usage folder in its own repository, and this project finds it there.
    assert (
        "- **Global folder** `../acme-ledger-repo/okf/acme-ledger-usage/`: How to use the Acme "
        "Ledger from another service" in global_context(out)
    )
    flat_out = " ".join(out.split())
    # The owner's three layers, in order: the work in progress, the project folder, the rest.
    layers = (
        "in this order: 1. The work in progress.",
        "2. The project folder, the first under Folders. It holds project knowledge",
        "3. The other folders, each when its description bears on the instruction.",
        "Folders lists this project's usage folders and the background folders",
        "Global Context, when that section appears below, lists knowledge folders",
    )
    order = [flat_out.index(layer) for layer in layers]
    assert order == sorted(order)
    assert "List it on every task, because it applies to everything done in this" in flat_out
    # One order, said once: the shared navigation text names no starting point of its own.
    assert "Start with" not in out.split("# How to Navigate context-db")[1].split("\n# ")[0]
    # Another project's usage knowledge is read the same way as this project's own.
    assert "One test applies to every folder: open what bears directly on the" in flat_out
    assert "look into it before you read that project's code" in flat_out
    marks = (
        "# Work In Progress",
        "# Folders",
        "# Global Context",
        "# Project Rules",
        "PCI-scoped",
        "# User Instruction",
    )
    order = [out.index(mark) for mark in marks]
    assert order == sorted(order)
    assert out.rstrip().endswith("add a refund endpoint")
    assert "<!--" not in out


def test_audit_says_what_to_report_only_after_the_reading_is_done(example):
    """The owner wants no "Schrodinger's cat problem": the report must not change what is read.

    So `prompt --audit` sends the usual message and one more step, to run the `audit` helper
    once the reading is done. Only that helper says what the report holds.
    """
    plain = run(example, "prompt", "add a refund endpoint").stdout
    audited = run(example, "prompt", "add a refund endpoint", "--audit").stdout
    before, rest = audited.split("# Audit\n", 1)
    step, after = rest.split("\n# Project Rules", 1)
    assert before + "# Project Rules" + after == plain  # the same reading, with or without it
    assert "# Global Context" in before
    step = " ".join(step.split())
    assert step.startswith("Once you have consulted context-db, and before you start on the")
    assert "context-db.py audit Do not run it sooner. Then follow what it prints." in step
    assert len(step.split()) < 40
    for word in ("report", "trail", "led you", "did not find"):
        assert word not in step, word  # nothing here says what will be asked
    assert audited.rstrip().endswith("add a refund endpoint")

    helper = run(example, "audit")
    assert helper.returncode == 0 and helper.stdout.startswith("# context-db Audit\n")
    told = " ".join(helper.stdout.split())
    assert "You were not told what the report holds before you read, so that it could not" in told
    assert "Read nothing more for it." in told
    assert "a file that turned out not to matter is what they most need to see" in told
    assert "what led you to it" in told and "What came from outside this project" in told
    assert "What you looked for and did not find, and any description that misled you" in told
    assert "Then carry out the instruction, without waiting for a reply." in told
    assert "`context-db audit, after the work`" in told
    assert "Which files the work rested on in the end, and which it did not need." in told

    # The agent runs the helper, so --help leaves it out. No other command takes the flag,
    # and with no task there is nothing to audit.
    assert "audit" not in help_commands(run(REPO, "--help").stdout)
    assert "# Audit" not in run(example, "prompt", "--audit").stdout
    for command in ("update", "wip", "maintain", "configure"):
        result = run(example, command, "--audit")
        assert result.returncode != 0 and "unrecognized arguments" in result.stdout, command

    # The front pages mention it, and the Commands page shows how the result is used.
    for path in (REPO / "README.md", REPO / "docs" / "index.md"):
        assert "#see-what-the-agent-read" in path.read_text(encoding="utf-8"), path
    commands = (REPO / "docs" / "commands.md").read_text(encoding="utf-8")
    shown = commands.split("### See what the agent read")[1].split("\n## ")[0]
    assert "```text\n/context-db prompt --audit\n\n" in shown
    assert "```text\n/context-db maintain\n\nLook at the audit result above." in shown


def test_prompt_starts_from_the_plans_that_bear_on_the_task(example):
    """No flag for picking work up: the list of plans is on every prompt, and the task names it."""
    out = run(example, "prompt", "carry on with the refund endpoint").stdout
    wip = " ".join(out.split("# Work In Progress")[1].split("# Folders")[0].split())
    assert "Open the plans that bear on the instruction before anything else." in wip
    assert "- [Refund endpoint](refund-endpoint.md). Started 2026-11-03" in wip
    start = " ".join(out.split("# How to Navigate")[0].split())
    assert "start with the plans it lists that bear on the instruction" in start


def test_the_docs_give_the_order_and_the_feature_branch_pattern():
    """The owner: wip first, then project knowledge, then the rest. And a branch for each effort."""
    commands = (REPO / "docs" / "commands.md").read_text(encoding="utf-8")
    steps = flat(commands.split("## /context-db prompt")[1].split("### See what the agent")[0])
    marks = ("The work in progress comes first.", "knowledge comes second", "These come last.")
    order = [steps.index(mark) for mark in marks]
    assert order == sorted(order)
    wip = commands.split("## /context-db wip")[1].split("## /context-db maintain")[0]
    pattern = flat(wip.split("### Feature branches")[1].split(":::{dropdown}")[0])
    assert "When you merge, the plan must not stay in the main branch's list." in pattern
    for path in (REPO / "README.md", REPO / "docs" / "index.md"):
        page = flat(path.read_text(encoding="utf-8"))
        assert "The plans for the work in progress come first, then your project" in page, path
        assert "then knowledge from outside the project." in page, path


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


# ── Global context ───────────────────────────────────────────────────────────

USAGE_NOTES = "../*/okc/*-usage.okf"
BY_INDEX = "(no description; it holds Orders, Refunds)"


def usage_notes(repo, description):
    """Notes the way another repository publishes them: <repo>/okc/<repo>-usage.okf/."""
    folder = repo / "okc" / f"{repo.name}-usage.okf"
    write(folder / f"{folder.name}.md", f"---\ntype: Folder\ndescription: {description}\n---\n")
    write(folder / "calling.md", doc(description=f"Calling {repo.name}"))
    return folder


@pytest.fixture
def workspace(tmp_path):
    """Repositories side by side. acme uses context-db; ledger and billing publish notes."""
    acme = tmp_path / "acme"
    acme.mkdir()
    result = run(acme, "configure", "--project", "acme", "--global-context", USAGE_NOTES)
    assert result.returncode == 0, result.stdout
    usage_notes(tmp_path / "ledger", "How to call the ledger")
    usage_notes(tmp_path / "billing", "How to call billing")
    return acme


def global_context(out):
    return out.split("# Global Context")[1].split("\n# ")[0]


def test_prompt_lists_the_folders_the_global_context_setting_matches(workspace):
    settings = (workspace / "context-db" / "configuration" / "settings.md").read_text()
    assert f"main_branch: main\nglobal_context: {USAGE_NOTES}\n---\n" in settings
    catalog(workspace.parent / "rates" / "okc" / "rates-usage.okf")
    write(workspace.parent / "stray" / "okc" / "file-usage.okf", "a file, not a folder\n")
    out = run(workspace, "prompt", "the task").stdout
    listed = [line for line in global_context(out).splitlines() if line.startswith("- ")]
    assert listed == [
        "- **Global folder** `../billing/okc/billing-usage.okf/`: How to call billing",
        "- **Global folder** `../ledger/okc/ledger-usage.okf/`: How to call the ledger",
        "- **Global folder** `../rates/okc/rates-usage.okf/`: " + BY_INDEX,
    ]
    assert "`global_context`\nsetting in `context-db/configuration/settings.md`" in out
    assert "context-db.py toc <folder>` lists one of them" in global_context(out)
    assert "Never edit one." in global_context(out)
    marks = ("# Folders", "# Global Context", "# Project Rules", "# User Instruction")
    order = [out.index(mark) for mark in marks]
    assert order == sorted(order)
    assert "Global Context, when that section appears below" in " ".join(out.split())
    listing = toc(workspace, "../ledger/okc/ledger-usage.okf")
    assert "* [Title](../ledger/okc/ledger-usage.okf/calling.md) - Calling ledger" in listing
    assert "Read from `../rates/okc/rates-usage.okf/index.md`" in toc(
        workspace, "../rates/okc/rates-usage.okf"
    )
    for command in ("update", "wip", "maintain"):
        assert "# Global Context" not in run(workspace, command, "x").stdout


def test_global_context_patterns_are_read_from_the_repository_root(workspace):
    subprocess.run(["git", "init", "-q"], cwd=str(workspace), check=True)
    deep = workspace / "src" / "api"
    deep.mkdir(parents=True)
    out = run(deep, "prompt", "x").stdout
    assert "- **Global folder** `../../../billing/okc/billing-usage.okf/`: How to" in out
    assert "- **Global folder** `../../../ledger/okc/ledger-usage.okf/`: How to" in out


def test_a_setting_with_several_values_is_a_yaml_list(workspace):
    """The owner: "Should this not be a list?" One value sits on the line; several are a list."""
    settings = workspace / "context-db" / "configuration" / "settings.md"
    one_line = f"global_context: {USAGE_NOTES}\n"
    assert one_line in settings.read_text()
    both = [
        "- **Global folder** `../billing/okc/billing-usage.okf/`: How to call billing",
        "- **Global folder** `../ledger/okc/ledger-usage.okf/`: How to call the ledger",
    ]
    written = (
        'global_context:\n  - ../billing/okc/*.okf\n  - "../ledger/okc/*.okf"\n',  # under the key
        "global_context:\n- ../billing/okc/*.okf\n- ../ledger/okc/*.okf\n",  # not indented
        "global_context: [../billing/okc/*.okf, '../ledger/okc/*.okf']\n",  # in brackets
    )
    for form in written:
        settings.write_text(settings.read_text().split("global_context:")[0] + form + "---\n")
        out = run(workspace, "prompt", "x").stdout
        assert [line for line in global_context(out).splitlines() if line.startswith("- ")] == both

    # configure writes several values as a list, and quotes one that YAML would misread.
    result = run(
        workspace, "configure", "--global-context", "*/okc/*.okf", "--global-context", "../x/*"
    )
    assert result.returncode == 0, result.stdout
    assert 'global_context:\n  - "*/okc/*.okf"\n  - ../x/*\n---\n' in settings.read_text()
    assert run(workspace, "prompt", "x").returncode == 0


def test_several_values_on_one_line_stop_the_commands(workspace):
    """The old form. It must not be read as one path with a space in it."""
    settings = workspace / "context-db" / "configuration" / "settings.md"
    good = settings.read_text()
    settings.write_text(good.replace(USAGE_NOTES, "okf/*-usage ../*/okf/*-usage"))
    said = (
        "Error: `global_context` in context-db/configuration/settings.md holds several values "
        "on one line. Write them as a list, one to a line:\n\n"
        "global_context:\n  - okf/*-usage\n  - ../*/okf/*-usage\n"
    )
    for command in ("prompt", "update", "wip", "maintain"):
        result = run(workspace, command, "x")
        assert result.returncode != 0 and said in result.stdout, command
    state = run(workspace, "configure").stdout
    assert "Several values on one line, which must be a list, so the other commands" in state
    assert "stop on it: `global_context`" in state
    result = run(workspace, "configure", "--usage-folder", "okf/a okf/b")
    assert result.returncode != 0 and "holds several values on one line" in result.stdout
    settings.write_text(good)
    result = run(workspace, "configure", "--usage-folder", "okf/a okf/b")
    assert result.returncode != 0 and "usage_folders:\n  - okf/a\n  - okf/b" in result.stdout
    result = run(
        workspace,
        "configure",
        "--local",
        "global_context=../a/*",
        "--local",
        "global_context=../b/*",
    )
    assert result.returncode == 0, result.stdout
    local = (workspace / "context-db" / "configuration" / "settings.local.md").read_text()
    assert "global_context:\n  - ../a/*\n  - ../b/*\n---\n" in local


def test_global_context_has_no_switch(workspace):
    """Patterns that are set are listed on every prompt. To stop that, take the patterns out."""
    assert "`../ledger/okc/ledger-usage.okf/`" in global_context(
        run(workspace, "prompt", "x").stdout
    )
    assert run(workspace, "configure", "--use-global-context", "false").returncode != 0
    assert run(workspace, "configure", "--local", "use_global_context=false").returncode != 0
    assert "use-global-context" not in run(REPO, "configure", "--help").stdout
    settings = workspace / "context-db" / "configuration" / "settings.md"
    settings.write_text(
        settings.read_text().replace("---\n\n", "use_global_context: false\n---\n\n", 1)
    )
    result = run(workspace, "prompt", "x")
    assert result.returncode != 0
    assert "a setting that context-db does not know: `use_global_context`" in result.stdout


def test_prompt_says_nothing_about_global_context_when_there_is_none(project):
    assert "# Global Context" not in run(project, "prompt", "x").stdout
    assert run(project, "configure", "--local", "global_context=../nowhere/*.okf").returncode == 0
    assert "# Global Context" not in run(project, "prompt", "x").stdout


def test_global_context_leaves_out_what_context_db_already_holds(workspace):
    cdb = workspace / "context-db"
    ledger = workspace.parent / "ledger"
    write(
        ledger / "context-db" / "ledger-project" / "ledger-project.md",
        "---\ntype: Folder\ndescription: The ledger's own notes\n---\n",
    )
    (cdb / "ledger-usage").symlink_to(ledger / "okc" / "ledger-usage.okf")
    result = run(
        workspace,
        "configure",
        "--global-context",
        "../*/context-db/*-project",
        "--global-context",
        USAGE_NOTES,
    )
    assert result.returncode == 0, result.stdout
    settings = (cdb / "configuration" / "settings.md").read_text()
    assert f"global_context:\n  - ../*/context-db/*-project\n  - {USAGE_NOTES}\n" in settings
    out = run(workspace, "prompt", "x").stdout
    listed = [line for line in global_context(out).splitlines() if line.startswith("- ")]
    assert listed == [
        "- **Global folder** `../ledger/context-db/ledger-project/`: The ledger's own notes",
        "- **Global folder** `../billing/okc/billing-usage.okf/`: How to call billing",
    ]
    folders = out.split("# Folders")[1].split("# Global Context")[0]
    assert "**Background folder** `context-db/ledger-usage/`: How to call the ledger" in folders
    assert out.count("acme-project/`") == 1


def test_configure_reports_and_asks_about_global_context(workspace, project):
    out = run(workspace, "configure").stdout
    assert (
        f"- Global context: `global_context: {USAGE_NOTES}` matches "
        "`../billing/okc/billing-usage.okf/`, `../ledger/okc/ledger-usage.okf/`" in out
    )
    assert " configure --global-context '<pattern>'\n" in out
    assert "use-global-context" not in out
    out = " ".join(run(project, "configure").stdout.split())
    assert "- Global context: no `global_context` setting" in out
    assert "Should `prompt` also list knowledge folders that are kept outside" in out
    assert "`../*/context-db/*-project/*-usage` matches the usage folder of every repository" in out
    assert "also offer to mount that folder" in out and "Do not mount its project folder" in out


def test_global_context_finds_usage_folders_inside_this_repository_and_next_to_it(workspace):
    """The layout of a team that keeps usage folders in okf/, outside context-db/."""
    result = run(
        workspace,
        "configure",
        "--usage-folder",
        "okf/{project}-usage",
        "--global-context",
        "okf/*-usage",
        "--global-context",
        "../*/okf/*-usage",
    )
    assert result.returncode == 0, result.stdout
    settings = (workspace / "context-db" / "configuration" / "settings.md").read_text()
    assert "usage_folders: okf/{project}-usage\n" in settings
    assert "global_context:\n  - okf/*-usage\n  - ../*/okf/*-usage\n" in settings
    usage_folder(workspace / "okf" / "acme-usage", "How to call acme")
    usage_folder(workspace / "okf" / "vendored-usage", "A copy kept in this repository")
    usage_folder(workspace.parent / "ledger" / "okf" / "ledger-usage", "How to call the ledger")
    write(workspace / "context-db" / "standards" / "standards.md", doc("Folder", "House rules"))
    out = run(workspace, "prompt", "x").stdout
    folders = out.split("# Folders")[1].split("\n# ")[0]
    assert [line.split("`:")[0] for line in folders.splitlines() if line.startswith("- ")] == [
        "- **Project folder** `context-db/acme-project/",
        "- **Usage folder** `okf/acme-usage/",
        "- **Background folder** `context-db/standards/",
    ]
    assert "- **Usage folder** `okf/acme-usage/`: How to call acme" in folders
    # This project's own usage folder matches both patterns and is not listed again.
    assert [line for line in global_context(out).splitlines() if line.startswith("- ")] == [
        "- **Global folder** `okf/vendored-usage/`: A copy kept in this repository",
        "- **Global folder** `../ledger/okf/ledger-usage/`: How to call the ledger",
    ]
    assert "lists knowledge folders that are kept outside `context-db/`" in " ".join(out.split())


# ── update ───────────────────────────────────────────────────────────────────


def test_update_puts_the_gate_before_the_mechanics(project):
    out = run(project, "update").stdout
    marks = ("nothing to change and stop", "## Where it goes", "# Folders", "# File Format")
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


def test_update_also_fixes_what_the_session_showed_to_be_wrong(project):
    """Housekeeping is part of every update, but only where the session gives a reason."""
    out = " ".join(run(project, "update").stdout.split())
    gate = out.split("## What belongs")[0]
    assert "What the notes you read turned out to be: one that is out of date" in gate
    assert "and the notes that turned out wrong or not needed, which you fix or delete" in gate
    assert "name them in a line and ask the user whether to clean them up" in gate
    assert 'say when in its first line, as in "Delete this once' in out
    finish = out.split("## Finish")[1]
    assert "cut every line that agent would not miss. Then run:" in finish
    assert "Tell the user in a line or two what you added, changed, and deleted." in finish


def test_update_brings_the_plan_the_session_worked_from_up_to_date(project):
    """No flag for it: a session that worked from a plan leaves it true, in two short places."""
    out = " ".join(run(project, "update").stdout.split())
    gate = out.split("## What belongs")[0]
    assert "for these things:" in gate
    assert (
        "Whether a plan in `context-db/demo-project/wip/` that this session worked from still "
        "says where the work stands." in gate
    )
    assert "If there is none of these, tell the user there is nothing to change and stop" in gate
    homes = out.split("Some things have a home of their own")[1].split("## Finish")[0]
    assert (
        "Bring a plan this session worked from, and its line in `wip.md`, up to date, and "
        "delete both once the work is finished." in homes
    )
    assert "--wip" not in run(project, "update", "--help").stdout
    assert run(project, "update", "--wip").returncode != 0


def test_update_names_the_home_of_what_does_not_go_in_the_main_tree(project):
    out = " ".join(run(project, "update").stdout.split())
    homes = out.split("Some things have a home of their own")[1].split("## Finish")[0]
    assert "`/context-db wip` handles the other plans." in homes
    assert "a usage folder, which this project does not have yet." in homes
    assert "an ON file in `context-db/configuration/`" in homes and "ask the user first" in homes
    assert "it belongs in that project's own usage folder, which you cannot write" in homes


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
    assert "# Commit" not in run(project, "update").stdout  # neither flag: no commit is asked for
    # A convenience and a matter of preference: `update --help` has the two flags, the overview not.
    usage = run(REPO, "update", "--help").stdout
    assert "--commit" in usage and "--push" in usage
    overview = run(REPO, "--help").stdout
    assert "--commit" not in overview and "--push" not in overview


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


def test_a_users_own_rules_follow_the_projects_rules(project):
    conf = project / "context-db" / "configuration"
    write(conf / "ON_PROMPT.md", "Keep changes compatible.\n")
    write(conf / "ON_PROMPT.local.md", "<!-- mine -->\nAnswer in one paragraph.\n")
    out = run(project, "prompt", "the task").stdout
    marks = (
        "# Project Rules\n\nKeep changes compatible.",
        "# User Rules\n\nThese are this user's own rules, from",
        "`context-db/configuration/ON_PROMPT.local.md`.",
        "follow these.\n\nAnswer in one paragraph.",
        "# User Instruction\n\nthe task",
    )
    order = [out.index(mark) for mark in marks]
    assert order == sorted(order)
    assert "mine" not in out
    for command in ("update", "wip", "maintain"):
        assert "Answer in one paragraph." not in run(project, command, "x").stdout


def test_a_users_own_rules_work_without_project_rules_and_keep_their_heading(project):
    conf = project / "context-db" / "configuration"
    (conf / "ON_UPDATE.md").unlink()
    write(conf / "ON_UPDATE.local.md", "# My Way\n\nNo emoji in commit messages.\n")
    out = run(project, "update", "--commit").stdout
    assert "# My Way\n\nNo emoji in commit messages." in out
    assert "# Project Rules" not in out and "# User Rules" not in out
    write(conf / "ON_UPDATE.local.md", "<!-- nothing yet -->\n")
    assert "My Way" not in run(project, "update").stdout


@pytest.mark.parametrize("command", context_db.ON_COMMANDS)
def test_every_command_has_a_project_and_a_user_rule_file(project, command):
    conf = project / "context-db" / "configuration"
    write(conf / f"ON_{command.upper()}.md", "From the project.\n")
    write(conf / f"ON_{command.upper()}.local.md", "From the user.\n")
    out = run(project, command, "x").stdout
    assert out.index("# Project Rules\n\nFrom the project.") < out.index("# User Rules\n\n")
    assert out.index("From the user.") < out.index("# User Instruction")


def test_one_gitignore_line_covers_every_per_user_file(tmp_path):
    subprocess.run(["git", "init", "-q"], cwd=str(tmp_path), check=True)
    write(tmp_path / ".gitignore", "context-db/configuration/settings.local.md\n")
    result = run(tmp_path, "configure", "--project", "demo", "--local", "python=python3")
    assert "Added context-db/configuration/*.local.md to .gitignore" in result.stdout
    conf = tmp_path / "context-db" / "configuration"
    for command in context_db.ON_COMMANDS:
        write(conf / f"ON_{command.upper()}.local.md", "Mine.\n")
    git(tmp_path, "add", "-A")
    staged = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        cwd=str(tmp_path),
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    ).stdout
    assert "ON_PROMPT.md" in staged and "settings.md" in staged
    assert ".local.md" not in staged.replace(".gitignore", "")
    assert "Added" not in run(tmp_path, "configure", "--project", "demo").stdout


def test_configure_shows_a_users_own_rules_too(project):
    conf = project / "context-db" / "configuration"
    write(conf / "ON_WIP.local.md", "Every plan lists the ticket number.\n")
    out = run(project, "configure").stdout
    rules = out.split("# Current Rules")[1]
    assert "ON_WIP.local.md`, this user's own, added after it" in rules
    assert "Every plan lists the ticket number." in rules
    assert "ON_PROMPT.local.md`, this user's own" not in rules
    assert "`ON_PROMPT.local.md` and the like" in out


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


# ── Usage folders ────────────────────────────────────────────────────────────


def usage_folder(folder, description="How to call demo from another project"):
    """A usage folder the way `update` leaves it: a descriptor and one note."""
    write(folder / f"{folder.name}.md", f"---\ntype: Folder\ndescription: {description}\n---\n")
    write(folder / "calling.md", doc("Rule", "What every caller must do"))
    return folder


def folder_lines(out):
    return out.split("# Folders")[1].split("\n# ")[0]


def test_update_writes_usage_knowledge_once_a_usage_folder_exists(project):
    """No flag for it. The rules for a usage folder join the message when there is one to write."""
    none = run(project, "update").stdout
    assert "# Usage Knowledge" not in none and "**Usage folder**" not in none
    flat_none = " ".join(none.split())
    assert "a usage folder, which this project does not have yet." in flat_none
    assert "Start one only when the user asks for it" in flat_none
    assert "create its descriptor, `context-db/demo-project/demo-usage/demo-usage.md`" in flat_none
    assert "context-db.py update` with the same instruction" in flat_none
    assert "using this project from outside" not in flat_none

    usage_folder(project / "context-db" / "demo-project" / "demo-usage")
    out = run(project, "update", "callers must send a key").stdout
    marks = (
        "# context-db Update",
        "- What this session changed or showed about using this project from outside.",
        "tell the user there is nothing to change and stop",
        "a usage folder (`context-db/demo-project/demo-usage/`). Usage Knowledge, below",
        "# Usage Knowledge",
        RULE,
        "# Folders",
        "# File Format",
        "# Project Rules",
        "# User Instruction",
    )
    order = [out.index(mark) for mark in marks]
    assert order == sorted(order)
    usage = " ".join(out.split("# Usage Knowledge")[1].split("\n# ")[0].split())
    assert "the bare minimum that an agent working in another project needs to know" in usage
    assert "It lives in a usage folder (`context-db/demo-project/demo-usage/`)" in usage
    assert "Most sessions change nothing here." in usage
    assert "Never reprint an API, a schema, a list of commands or flags" in usage
    assert "What only the code or its comments say does not count as told" in usage
    assert "Project knowledge stays in the project folder." in usage
    assert "context-db.py toc <folder>` on a usage folder first" in usage
    assert "starting with its descriptor, which Folders names" in usage
    assert "do not start a folder that is not listed" in usage
    assert 'Call the project by its name, never "this project" or "here".' in usage
    assert out.rstrip().endswith("# User Instruction\n\ncallers must send a key")
    pushed = run(project, "update", "--push").stdout
    assert (
        pushed.index("# Usage Knowledge") < pushed.index("# File Format") < pushed.index("# Commit")
    )


def test_maintain_covers_the_usage_folders_once_one_exists(project):
    """No flag for it: the sweep takes in the usage folders, judged for their own reader."""
    none = run(project, "maintain").stdout
    assert "# How to Check the Usage Folders" not in none and "**Usage folder**" not in none
    flat_none = " ".join(none.split())
    assert (
        "look at all of it: the project folder, `context-db/demo-project/`, with its plans, "
        "and the usage folders." in flat_none
    )
    assert "And the usage folders, if How to Check the Usage Folders appears below." in flat_none
    usage_folder(project / "context-db" / "demo-project" / "demo-usage")
    out = run(project, "maintain", "the calling rules").stdout
    marks = (
        "# context-db Maintain",
        RULE,
        "# Git History",
        "# Folders",
        "# How to Check the Usage Folders",
        "# File Format",
        "# User Instruction",
    )
    order = [out.index(mark) for mark in marks]
    assert order == sorted(order)
    usage = " ".join(out.split("# How to Check the Usage Folders")[1].split("\n# ")[0].split())
    assert "The usage folders (`context-db/demo-project/demo-usage/`) hold usage knowledge" in usage
    assert "one who uses this project and does not read its insides" in usage
    assert "move it to the project folder" in usage
    assert "A link that leaves its usage folder becomes a URL" in usage
    assert "**Wrong** is judged by the project as it is now." in usage
    assert out.rstrip().endswith("the calling rules")


def test_the_usage_folder_is_listed_once_it_exists(project):
    assert "Usage folder" not in folder_lines(run(project, "prompt", "x").stdout)
    usage_folder(project / "context-db" / "demo-project" / "demo-usage")
    line = "- **Usage folder** `context-db/demo-project/demo-usage/`: How to call demo from"
    for args in (("prompt", "x"), ("update",), ("maintain",)):
        assert line in folder_lines(run(project, *args).stdout), args
    assert "does not exist yet" not in folder_lines(run(project, "update").stdout)
    listing = toc(project)
    assert "* [demo-usage](context-db/demo-project/demo-usage/) - How to call demo" in listing
    assert run(project, "toc", "--check").returncode == 0
    assert "Look into this project's own usage folder, if Folders lists one, when the" in (
        " ".join(run(project, "prompt", "x").stdout.split())
    )


def test_the_usage_folders_setting_keeps_it_somewhere_else(project):
    result = run(project, "configure", "--usage-folder", "okf/{project}-usage")
    assert result.returncode == 0, result.stdout
    settings = (project / "context-db" / "configuration" / "settings.md").read_text()
    assert "main_branch: main\nusage_folders: okf/{project}-usage\n---\n" in settings
    assert usage_place(project) == "okf/demo-usage/"
    assert "Usage folder" not in folder_lines(run(project, "prompt", "x").stdout)
    usage = usage_folder(project / "okf" / "demo-usage")
    for args in (("prompt", "x"), ("update",), ("maintain",)):
        out = run(project, *args).stdout
        assert "- **Usage folder** `okf/demo-usage/`: How to call demo" in folder_lines(out), args
    assert "It lives in a usage folder (`okf/demo-usage/`)" in " ".join(
        run(project, "update").stdout.split()
    )
    shutil.rmtree(usage)
    # One user keeps theirs elsewhere, and the path is read from the repository root.
    assert run(project, "configure", "--local", "usage_folders=notes/mine").returncode == 0
    subprocess.run(["git", "init", "-q"], cwd=str(project), check=True)
    (project / "src").mkdir()
    assert usage_place(project / "src") == "../notes/mine/"


def test_a_project_can_keep_more_than_one_usage_folder(project):
    """One for each group of users, each a folder that stands on its own."""
    places = ("okf/{project}-usage", "okf/{project}-admin-usage")
    result = run(project, "configure", "--usage-folder", places[0], "--usage-folder", places[1])
    assert result.returncode == 0, result.stdout
    settings = (project / "context-db" / "configuration" / "settings.md").read_text()
    assert f"usage_folders:\n  - {places[0]}\n  - {places[1]}\n---\n" in settings
    usage_folder(project / "okf" / "demo-usage", "How to call demo")
    out = run(project, "update").stdout
    both = "`okf/demo-usage/`, `okf/demo-admin-usage/`"
    assert f"It lives in a usage folder ({both})" in " ".join(out.split())
    assert "never the same thing in two" in " ".join(out.split())
    assert "- **Usage folder** `okf/demo-usage/`: How to call demo" in folder_lines(out)
    assert (
        "- **Usage folder** `okf/demo-admin-usage/` does not exist yet. "
        "Its descriptor will be `okf/demo-admin-usage/demo-admin-usage.md`." in folder_lines(out)
    )
    assert "demo-admin-usage" not in folder_lines(run(project, "prompt", "x").stdout)

    admin = usage_folder(project / "okf" / "demo-admin-usage", "How to run demo")
    listed = folder_lines(run(project, "prompt", "x").stdout).splitlines()
    assert [line for line in listed if line.startswith("- **Usage folder**")] == [
        "- **Usage folder** `okf/demo-usage/`: How to call demo",
        "- **Usage folder** `okf/demo-admin-usage/`: How to run demo",
    ]
    out = " ".join(run(project, "maintain").stdout.split())
    assert f"The usage folders ({both}) hold usage knowledge" in out
    state = run(project, "configure").stdout
    assert (
        f"- Usage folders, from `usage_folders: {places[0]} {places[1]}`: "
        "`okf/demo-usage/` (exists), `okf/demo-admin-usage/` (exists)" in state
    )

    # Each is checked, and each is read on its own, so a link may not cross between them.
    result = run(project, "toc", "--check")
    assert result.returncode == 0, result.stdout
    for name in ("context-db/demo-project", "okf/demo-usage", "okf/demo-admin-usage"):
        assert f"{name}/ is a conformant OKF" in result.stdout
    write(admin / "start.md", doc(body="See [calling](../demo-usage/calling.md).\n"))
    result = run(project, "toc", "--check")
    assert result.returncode == 1
    assert "start.md: link `../demo-usage/calling.md` leaves the usage folder" in result.stdout
    (admin / "start.md").unlink()

    # A pattern that finds usage folders never lists this project's own as someone else's.
    assert run(project, "configure", "--global-context", "okf/*-usage").returncode == 0
    assert "# Global Context" not in run(project, "prompt", "x").stdout


def test_a_usage_folder_at_the_top_of_context_db_is_not_a_background_folder(project):
    assert run(project, "configure", "--usage-folder", "context-db/demo-usage").returncode == 0
    cdb = project / "context-db"
    usage_folder(cdb / "demo-usage")
    write(cdb / "standards" / "standards.md", doc("Folder", "House rules"))
    folders = folder_lines(run(project, "prompt", "x").stdout)
    assert "- **Usage folder** `context-db/demo-usage/`: How to call demo" in folders
    assert folders.count("Background folder") == 1 and "demo-usage" not in folders.split("Bac")[1]
    write(cdb / "demo-usage" / "index.md", "# Files\n\n* [Gone](gone.md) - Long deleted\n")
    assert "Long deleted" not in toc(project, "context-db/demo-usage")  # never read: it is ours
    assert "Read from `context-db/standards/index.md`" not in toc(project, "context-db/standards")


def test_the_check_covers_a_usage_folder_kept_outside_the_project_folder(project):
    assert run(project, "configure", "--usage-folder", "okf/demo-usage").returncode == 0
    usage = usage_folder(project / "okf" / "demo-usage")
    result = run(project, "toc", "--check")
    assert result.returncode == 0, result.stdout
    assert "context-db/demo-project/ is a conformant OKF" in result.stdout
    assert "okf/demo-usage/ is a conformant OKF" in result.stdout
    # A published folder may carry an index.md for readers that are not context-db.
    write(usage / "index.md", "# Files\n\n* [Calling](calling.md) - What every caller must do\n")
    result = run(project, "toc", "--check")
    assert result.returncode == 0 and "WARNING" not in result.stdout, result.stdout
    write(usage / "index.md", "# Files\n\n* [Gone](gone.md) - Long deleted\n")
    write(usage / "bad.md", "# No frontmatter\n")
    result = run(project, "toc", "--check")
    assert result.returncode == 1
    assert "okf/demo-usage/index.md: does not list `bad.md`, `calling.md`" in result.stdout
    assert "okf/demo-usage/index.md: lists `okf/demo-usage/gone.md`, which is not" in result.stdout
    assert "okf/demo-usage/bad.md: no YAML frontmatter" in result.stdout
    assert "context-db/demo-project/ is a conformant OKF" in result.stdout
    assert "\n1 error(s). Fix them, then run:  python3 " in result.stdout
    assert result.stdout.rstrip().endswith(" toc --check")
    assert "Long deleted" not in toc(project, "okf/demo-usage")
    result = run(project, "toc", "okf/demo-usage", "--check")
    assert result.returncode == 1 and "demo-project" not in result.stdout
    assert result.stdout.rstrip().endswith(" toc --check okf/demo-usage")


@pytest.mark.parametrize("place, up", [("context-db/demo-project/demo-usage", 3), ("okf/u", 2)])
def test_a_usage_note_links_only_inside_the_usage_folder(project, place, up):
    if not place.startswith("context-db"):
        assert run(project, "configure", "--usage-folder", place).returncode == 0
    usage = usage_folder(project.joinpath(*place.split("/")))
    write(project / "src" / "client.py", "x = 1\n")
    write(usage / "start.md", doc(body="See [the rules](./calling.md) and [more](deep/more.md).\n"))
    write(usage / "deep" / "deep.md", doc("Folder", "The details", body=""))
    write(usage / "deep" / "more.md", doc(body="Back to [the start](../start.md).\n"))
    result = run(project, "toc", "--check")
    assert result.returncode == 0, result.stdout
    link = "../" * up + "src/client.py"
    write(usage / "deep" / "more.md", doc(body=f"See [the client](../{link}).\n"))
    result = run(project, "toc", "--check")
    assert result.returncode == 1
    assert f"deep/more.md: link `../{link}` leaves the usage folder" in result.stdout
    assert "link only to files inside it" in result.stdout
    # A note in the project folder may link out to the code, and into the usage folder.
    (usage / "deep" / "more.md").unlink()
    (usage / "deep" / "deep.md").unlink()
    write(usage / "start.md", doc(body="See [the rules](./calling.md).\n"))
    here = project / "context-db" / "demo-project" / "internals.md"
    inside = os.path.relpath(usage / "calling.md", here.parent)
    write(here, doc(body=f"See [the client](../../src/client.py) and [the rules]({inside}).\n"))
    result = run(project, "toc", "--check")
    assert result.returncode == 0, result.stdout


@pytest.mark.parametrize("place", ["context-db/demo-project/demo-usage", "okf/demo-usage"])
def test_git_history_covers_the_project_folder_and_the_usage_folders(project, place):
    if not place.startswith("context-db"):
        assert run(project, "configure", "--usage-folder", place).returncode == 0
    usage = usage_folder(project.joinpath(*place.split("/")))
    write(usage / "start.md", doc(body="See [the rules](./calling.md).\n"))
    write(project / "context-db" / "demo-project" / "wip" / "plan.md", doc("Plan", "A plan"))
    write(project / "src" / "a.py", "x = 1\n")
    git(project, "init", "-q", "-b", "main")
    git(project, "add", "-A")
    git(project, "commit", "-q", "-m", "base")
    write(usage / "calling.md", doc("Rule", "What every caller must do", body="# Changed\n"))
    git(project, "add", "-A")
    git(project, "commit", "-q", "-m", "a usage note changes")
    write(project / "src" / "a.py", "x = 2\n")
    git(project, "add", "-A")
    git(project, "commit", "-q", "-m", "the code moves on")

    out = run(project, "maintain").stdout
    history = out.split("# Git History")[1].split("# Folders")[0]
    assert "every note in the project folder and the usage folders" in " ".join(history.split())
    rows = [line for line in history.splitlines() if line.startswith("- `")]
    assert sorted(row.split("`")[1] for row in rows) == sorted(
        ["context-db/demo-project/retry-policy.md", f"{place}/calling.md", f"{place}/start.md"]
    )
    for row in rows:
        assert "; 1 commits to the project since" in row  # a change to a usage note is not one
        assert "linked files" not in row  # a link to another usage note is not a link to the code
    assert "wip/plan.md" not in history  # a plan is checked against the branch instead
    assert "# How to Check the Plans" in out and "# Git State" in out


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
    marks = ("# context-db Maintain", "# Folders", "# File Format", "legal/", "# User Instruction")
    order = [out.index(mark) for mark in marks]
    assert order == sorted(order)
    assert out.rstrip().endswith("the api notes")


def test_maintain_without_config_asks_for_configure(tmp_path):
    (tmp_path / "context-db").mkdir()
    assert "/context-db configure" in run(tmp_path, "maintain").stdout


RULE = "# No Duplication"
SMALL = "# Keep context-db Small"
WRITES_NOTES = (
    ("update",),
    ("maintain",),
    ("wip",),
    ("wip", "--maintain"),
)
READS_OR_WRITES_NOTES = (("prompt", "x"),) + WRITES_NOTES


def test_every_command_that_reads_or_writes_notes_repeats_the_rule(project):
    for args in READS_OR_WRITES_NOTES:
        out = run(project, *args).stdout
        assert out.count(RULE) == 1, args
        rule = " ".join(out.split(RULE)[1].split("\n# ")[0].split())
        assert rule.startswith(
            "context-db does not duplicate information found in the project's assets (code, code "
            "comments, configs, docs)."
        ), args
        assert "or anything a code comment, the README, or the docs already say" in rule, args
    for args in (("wip", "--list"), ("configure",)):
        assert RULE not in run(project, *args).stdout


def test_every_command_that_writes_notes_is_told_to_keep_the_knowledge_base_small(project):
    """The second rule: the writer looks after the knowledge base and does not only add to it."""
    for args in WRITES_NOTES:
        out = run(project, *args).stdout
        assert out.count(SMALL) == 1, args
        marks = (RULE, SMALL, "# How to Navigate context-db", "# File Format")
        order = [out.index(mark) for mark in marks]
        assert order == sorted(order), args
        rule = " ".join(out.split(SMALL)[1].split("\n# ")[0].split())
        assert "Leaving it smaller is as good a result as leaving it larger." in rule
        for line in (
            "- Write the least that does the job",
            "- One fact, one place.",
            "- Replace, do not append.",
            "- Delete what is no longer needed",
            "When it is not obvious how much to clean up, ask the user how far to go.",
        ):
            assert line in rule, (args, line)
    for args in (("prompt", "x"), ("wip", "--list"), ("wip", "--clear"), ("configure",)):
        assert SMALL not in run(project, *args).stdout, args


def test_every_command_that_reads_notes_says_how_to_navigate(project):
    for args in READS_OR_WRITES_NOTES:
        out = run(project, *args).stdout
        assert out.count("# How to Navigate context-db") == 1, args
        assert "context-db.py toc <folder>" in out, args
    prompts = REPO / "skill" / "context-db" / "prompts"
    mentions = sorted(p.name for p in prompts.glob("*.md") if "index.md" in p.read_text())
    assert mentions == ["format.md", "navigate.md"]  # do not create one, and do not read one
    navigate = " ".join((prompts / "navigate.md").read_text().split())
    assert "or reading an `index.md` that the folder may carry" in navigate


def test_maintain_enforces_the_rule_against_code_and_comments(project):
    out = " ".join(run(project, "maintain").stdout.split())
    assert "Your main job is to enforce No Duplication, below" in out
    assert "open the code it is about, comments included" in out
    assert "do not edit the code yourself" in out
    assert "Git History, below, says which notes the code has moved furthest past" in out


def test_maintain_cuts_back_what_is_no_longer_needed_and_shapes_the_rest(project):
    out = " ".join(run(project, "maintain").stdout.split())
    assert "Your second job is Keep context-db Small: cut back what is no longer" in out
    looks_for = out.split("## What to look for")[1].split("## How to change it")[0]
    marks = (
        "**Repeats the project.**",
        "**Outlived its use.**",
        "**Says too much.**",
        "**Duplicated.**",
        "**Not worth keeping.**",
        "**Several topics in one file.**",
    )
    order = [looks_for.index(mark) for mark in marks]
    assert order == sorted(order)
    assert "A note that repeats a background folder goes" in looks_for
    assert "For this command, every note in scope bears on the task." in looks_for
    assert "leave the note until the comment is there" in looks_for
    assert "For any other note you want to delete, list it and ask the user first." in out
    assert "Cutting a note down is not deleting it." in out


def test_maintain_ranks_notes_by_how_far_the_code_moved(project):
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
    out = run(project, "maintain").stdout
    history = out.split("# Git History")[1].split("# Folders")[0]
    rows = [line for line in history.splitlines() if line.startswith("- `")]
    assert "retry-policy.md`: last changed" in rows[0]
    assert "1 commits to the project since; linked files changed since: `src/retry.py`" in rows[0]
    assert "naming.md`" in rows[1] and "linked files" not in rows[1]
    assert rows[-1].endswith("fresh.md`: not committed yet")
    assert "Age alone proves nothing." in history
    assert out.index(RULE) < out.index("# Git History") < out.index("# Folders")


def test_maintain_outside_git(project):
    """Git is the standard for maintain. Without it the agent works from the files alone."""
    out = " ".join(run(project, "maintain").stdout.split())
    assert "so there is no history to read. Maintain the knowledge base without it." in out


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
    assert "Record where the work in progress stands" in flat
    assert "today, " + datetime.date.today().isoformat() + ", on `feature/x`" in flat
    assert "- [x-plan](x-plan.md). Started 2026-11-01" in out
    assert "# How Work In Progress Is Kept" in out and "# File Format" in out
    assert "# Git State" not in out
    assert out.rstrip().endswith("plan the x work")
    # The owner's pattern: a branch for each effort, and no plan left on the main branch.
    kept = " ".join(out.split("# How Work In Progress Is Kept")[1].split("\n# ")[0].split())
    branches = kept.split("## Feature branches")[1]
    assert "A useful pattern is one feature branch for each effort" in branches
    assert "Once the branch is merged, `main` must not list the effort" in branches
    assert "or on `main` straight after it." in branches
    assert len(branches.split()) < 70
    # It describes a pattern and orders no commit. A trial agent read "committed on that
    # branch" as a possible order, and "the last commit before the merge" found none to act on.
    assert "commit" not in branches


def test_wip_maintain_shows_git_state_and_the_list(project):
    git(project, "init", "-q", "-b", "main")
    git(project, "add", "-A")
    git(project, "commit", "-q", "-m", "base")
    git(project, "checkout", "-q", "-b", "feature/x")
    write(project / "src.py", "print('hi')\n")
    git(project, "add", "-A")
    git(project, "commit", "-q", "-m", "add src")
    add_plan(project)
    out = run(project, "wip", "--maintain").stdout
    assert "# context-db Wip Maintain" in out
    assert "- Current branch: `feature/x`" in out
    assert "- Main branch: `main`" in out
    assert "Work has landed when it is merged into `main`" in out
    # On the main branch a merged plan names another branch, and it still goes.
    assert "has all landed is finished, whichever branch it names: delete it" in " ".join(
        out.split()
    )
    assert "add src" in out and "src.py" in out
    assert "x-plan.md" in out.split("git status --short")[1]
    assert "- [x-plan](x-plan.md)" in out.split("# Work In Progress")[1]
    marks = ("# context-db Wip Maintain", "# How to Check the Plans", "# Git State", "# Work In Pr")
    order = [out.index(mark) for mark in marks]
    assert order == sorted(order)
    # `maintain` checks the plans the same way, as part of its sweep.
    swept = run(project, "maintain").stdout
    for mark in marks[1:]:
        assert mark in swept, mark
    assert "`/context-db wip --maintain` does this part alone." in " ".join(swept.split())
    assert run(project, "wip", "--cleanup").returncode != 0


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
    out = run(project, "wip", "--maintain").stdout
    assert "## Recent commits" in out and "only commit" in out


def test_wip_says_so_when_the_main_branch_does_not_exist(project):
    git(project, "init", "-q", "-b", "trunk")
    git(project, "add", "-A")
    git(project, "commit", "-q", "-m", "base")
    out = run(project, "wip", "--maintain").stdout
    assert "main branch `main` does not exist" in out
    assert "context-db/configuration/settings.md" in out
    assert "base" in out


def test_wip_outside_git(project):
    assert "Not a git repository" in run(project, "wip", "--maintain").stdout


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
    assert "context-db/configuration/*.local.md\n" in gitignore

    write(cdb / "configuration" / "ON_PROMPT.md", "mine\n")
    settings.write_text(settings.read_text() + "\nA note of my own.\n")
    again = run(tmp_path, "configure", "--main-branch", "main")
    assert again.returncode == 0
    assert (cdb / "configuration" / "ON_PROMPT.md").read_text() == "mine\n"
    content = settings.read_text()
    assert "main_branch: main\n" in content and "python: python3.11\n" in content
    assert content.endswith("A note of my own.\n")
    assert (tmp_path / ".gitignore").read_text().count("*.local.md") == 1


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
        ("--project", "demo", "--local", "use_global_context=false"),  # no longer a setting
    ):
        assert run(tmp_path, "configure", *args).returncode != 0
    assert not (tmp_path / "context-db").exists()


def test_configure_with_settings_catches_a_project_name_given_with_its_suffix(tmp_path):
    write(tmp_path / "context-db" / "acme-project" / "acme-project.md", doc("Folder", "Acme"))
    result = run(tmp_path, "configure", "--project", "acme-project")
    assert result.returncode != 0
    assert "--project acme" in result.stdout
    assert not (tmp_path / "context-db" / "acme-project-project").exists()


# ── Settings files that override ─────────────────────────────────────────────


def settings_file(path, **values):
    """A settings file kept outside the project, written by hand. A list becomes a YAML list."""
    header = "".join(
        f"{key}:\n" + "".join(f"  - {item}\n" for item in value)
        if isinstance(value, list)
        else f"{key}: {value}\n"
        for key, value in values.items()
    )
    write(path, f"---\n{header}---\n\nShared by every project of the team.\n")
    return path


def name_settings_files(repo, names, local=False):
    """Add a `settings_files` line by hand, the only way there is."""
    name = "settings.local.md" if local else "settings.md"
    path = repo / "context-db" / "configuration" / name
    content = path.read_text() if path.exists() else "---\n---\n"
    path.write_text(content.replace("---\n", f"---\nsettings_files: {names}\n", 1))


def usage_place(repo):
    """Where the usage folder is to go, as `update` says it while there is none yet."""
    out = " ".join(run(repo, "update").stdout.split())
    descriptor = out.split("create its descriptor, `")[1].split("`")[0]
    return descriptor.rsplit("/", 1)[0] + "/"


def test_a_named_settings_file_overrides_the_file_that_names_it(workspace):
    conf = workspace / "context-db" / "configuration"
    team = workspace.parent / "team" / "context-db.md"
    settings_file(team, usage_folders="okf/{project}-usage", global_context="../nowhere/*")
    assert usage_place(workspace) == "context-db/acme-project/acme-usage/"
    assert "# Global Context" in run(workspace, "prompt", "x").stdout
    name_settings_files(workspace, "../team/context-db.md")
    assert usage_place(workspace) == "okf/acme-usage/"
    assert "# Global Context" not in run(workspace, "prompt", "x").stdout

    # Your own file is read after the team's, and a file it names is read last of all.
    assert run(workspace, "configure", "--local", "usage_folders=mine/acme-usage").returncode == 0
    assert usage_place(workspace) == "mine/acme-usage/"
    mine = settings_file(workspace.parent / "me.md", usage_folders="last/{project}-usage")
    name_settings_files(workspace, str(mine), local=True)  # an absolute path works too
    assert usage_place(workspace) == "last/acme-usage/"

    # configure rewrites settings.md and keeps the line it did not write.
    assert run(workspace, "configure", "--main-branch", "trunk").returncode == 0
    settings = (conf / "settings.md").read_text()
    assert (
        "main_branch: trunk\n" in settings and "settings_files: ../team/context-db.md\n" in settings
    )
    state = run(workspace, "configure").stdout.split("# Detected State")[1]
    named_by = "named by `context-db/configuration/settings"
    marks = (
        "- Shared settings `context-db/configuration/settings.md`: `project: acme`",
        f"- Settings file `../team/context-db.md`, {named_by}.md`: `usage_folders: okf/",
        "- Your own settings `context-db/configuration/settings.local.md`: ",
        f"- Settings file `../me.md`, {named_by}.local.md`: ",
        "- Usage folders, from `usage_folders: last/{project}-usage`: `last/acme-usage/` (does",
    )
    order = [state.index(mark) for mark in marks]
    assert order == sorted(order)


def test_a_named_settings_file_that_cannot_be_read_stops_every_command_but_configure(workspace):
    team = settings_file(workspace.parent / "team.md", main_branch="trunk")
    name_settings_files(workspace, "../team.md")
    assert run(workspace, "prompt", "x").returncode == 0
    for broken, problem in (("no frontmatter\n", "has no `---` block"), (None, "does not exist")):
        team.unlink() if broken is None else team.write_text(broken)
        for command in ("prompt", "update", "wip", "maintain"):
            result = run(workspace, command, "x")
            assert result.returncode != 0, command
            assert f"Error: ../team.md {problem}" in result.stdout
            assert (
                "The `settings_files` line in context-db/configuration/settings.md names it."
                in result.stdout
            )
            assert "Traceback" not in result.stdout
        result = run(workspace, "configure")
        assert result.returncode == 0
        assert (
            "- Settings file `../team.md`, named by `context-db/configuration/settings.md`: "
            + problem
            in result.stdout
        )
        assert run(workspace, "toc", "context-db/acme-project").returncode == 0


def test_settings_files_can_name_more_and_cannot_loop(workspace):
    one, two = workspace.parent / "one.md", workspace.parent / "two.md"
    settings_file(one, usage_folders="one/{project}-usage", settings_files="../two.md")
    settings_file(
        two, usage_folders="two/{project}-usage", settings_files=["../one.md", "../two.md"]
    )
    name_settings_files(workspace, "../one.md")
    assert usage_place(workspace) == "two/acme-usage/"  # read after the file that names it
    state = run(workspace, "configure").stdout.split("# Detected State")[1]
    assert state.count("- Settings file `../one.md`") == 1
    assert "- Settings file `../two.md`, named by `../one.md`:" in state
    assert state.count("- Settings file `../two.md`") == 1


def test_no_command_sets_the_settings_files_line(workspace):
    result = run(workspace, "configure", "--local", "settings_files=../team.md")
    assert result.returncode != 0 and "--local takes KEY=VALUE" in result.stdout
    assert "settings_files" not in result.stdout.split("KEY is one of")[1]
    assert run(workspace, "configure", "--settings-file", "../team.md").returncode != 0
    assert "settings_file" not in run(REPO, "configure", "--help").stdout
    assert "--usage-folder" in run(REPO, "configure", "--help").stdout
    body = (workspace / "context-db" / "configuration" / "settings.md").read_text()
    assert "- settings_files: more settings files to read" in body  # the file says how
    assert "such as okf/{project}-usage. {project} stands for the project name" in " ".join(
        body.split()
    )


def test_a_key_that_is_not_a_setting_stops_the_commands(workspace):
    """Settings files are written by hand, so a misspelt key must not pass in silence."""
    conf = workspace / "context-db" / "configuration"
    settings = conf / "settings.md"
    good = settings.read_text()
    settings.write_text(good.replace("---\n\n", "usage_folder: okf/acme-usage\n---\n\n", 1))
    said = (
        "Error: context-db/configuration/settings.md has a setting that context-db does not "
        "know: `usage_folder`. The settings are project, python, main_branch, usage_folders, "
        "global_context, settings_files."
    )
    for command in ("prompt", "update", "wip", "maintain"):
        result = run(workspace, command, "x")
        assert result.returncode != 0, command
        assert said in result.stdout and "Traceback" not in result.stdout
    state = run(workspace, "configure")  # the repair tool still runs, and points at it
    assert state.returncode == 0
    assert "Not a setting, so the other commands stop on it: `usage_folder`" in state.stdout
    result = run(workspace, "configure", "--main-branch", "trunk")
    assert result.returncode != 0 and said in result.stdout
    assert "main_branch: main\n" in settings.read_text()  # and nothing was written

    # The same holds for a file that settings.md names, and for your own.
    settings.write_text(good)
    team = settings_file(workspace.parent / "team.md", usage_folderz="okf/{project}-usage")
    name_settings_files(workspace, "../team.md")
    result = run(workspace, "prompt", "x")
    assert result.returncode != 0
    assert "Error: ../team.md has a setting that context-db does not know: `usage_folderz`" in (
        result.stdout
    )
    team.unlink()
    settings.write_text(good)
    write(conf / "settings.local.md", "---\ncolour: blue\n---\n")
    result = run(workspace, "configure", "--local", "python=python3")
    assert result.returncode != 0 and "settings.local.md has a setting" in result.stdout


# ── The shipped trees stay clean ─────────────────────────────────────────────


def test_example_project_and_shared_folders_are_conformant(example):
    result = run(example, "toc", "--check")
    assert result.returncode == 0 and "WARNING" not in result.stdout, result.stdout
    shared = example.parent / "shared"
    for name in ("coding-standards", "git-standards"):
        result = run(shared, "toc", name, "--check")
        assert result.returncode == 0, result.stdout
    result = run(example, "toc", "../acme-ledger-repo/okf/acme-ledger-usage", "--check")
    assert result.returncode == 0 and "WARNING" not in result.stdout, result.stdout


def test_this_repos_own_knowledge_base_is_conformant():
    result = run(REPO, "toc", "--check")
    assert result.returncode == 0, result.stdout


def test_this_repo_and_the_example_are_set_up_by_the_current_skill():
    """Both run the skill in skill/, and carry its current settings comment and starter text."""
    starters = SCRIPT.parent / "starters"
    comment = re.compile(r"(?s)\A<!--.*?-->")
    note = (starters / "AGENTS.md").read_text(encoding="utf-8").strip()
    for root in (REPO, REPO / "example" / "acme-payments-repo"):
        assert (root / ".claude" / "skills" / "context-db").resolve() == SCRIPT.parent, root
        assert note in (root / "AGENTS.md").read_text(encoding="utf-8"), root
        conf = root / "context-db" / "configuration"
        body = (conf / "settings.md").read_text(encoding="utf-8").split("---\n", 2)[2]
        assert body.strip() == context_db.text(context_db.SETTINGS_BODY), conf
        for command in context_db.ON_COMMANDS:
            name = f"ON_{command.upper()}.md"
            current = comment.match((starters / name).read_text(encoding="utf-8")).group()
            assert (conf / name).read_text(encoding="utf-8").startswith(current), conf / name


def shipped_documents():
    roots = [
        REPO / "context-db" / "context-db-project",
        REPO / "example" / "acme-payments-repo" / "context-db" / "acme-payments-project",
        REPO / "example" / "acme-ledger-repo" / "okf",
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


def test_the_packaged_entry_point_runs_the_script_beside_it(tmp_path):
    """pyproject.toml installs skill/context-db/cli.py's main() as the `context-db` command."""
    entry = SCRIPT.parent / "cli.py"
    expected = run(tmp_path, "--help")
    result = run(tmp_path, "--help", script=entry)
    assert result.returncode == 0, result.stdout
    assert result.stdout.replace("cli.py", "context-db.py") == expected.stdout
    configured = run(tmp_path, "configure", "--project", "demo", script=entry)
    assert configured.returncode == 0, configured.stdout
    assert (tmp_path / "context-db" / "configuration" / "settings.md").is_file()


def test_installed_command_prints_itself_as_the_next_command(tmp_path):
    """Started as `context-db`, the commands it prints name it, not python and the script."""
    entry = SCRIPT.parent / "cli.py"
    command = tmp_path / "bin" / "context-db"
    write(
        command,
        "import importlib.util\n"
        f"spec = importlib.util.spec_from_file_location('cli', {str(entry)!r})\n"
        "cli = importlib.util.module_from_spec(spec)\n"
        "spec.loader.exec_module(cli)\n"
        "cli.main()\n",
    )
    project = tmp_path / "project"
    project.mkdir()
    assert run(project, "configure", "--project", "demo", script=command).returncode == 0
    out = run(project, "prompt", "x", script=command).stdout
    assert "../bin/context-db toc" in out
    assert "context-db.py" not in out
    assert "context-db.py toc" in run(project, "prompt", "x").stdout  # run as the script
