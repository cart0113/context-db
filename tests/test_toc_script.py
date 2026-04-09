#!/usr/bin/env python3
"""
Test suite for context-db-generate-toc.sh

Creates temp directories with various frontmatter styles, runs the TOC
script, and asserts expected output. Covers YAML scalar styles an LLM
is likely to produce.
"""

import os
import subprocess
import tempfile
import textwrap
import unittest

SCRIPT = os.path.join(
    os.path.dirname(__file__),
    "..",
    ".claude",
    "skills",
    "context-db-manual",
    "scripts",
    "context-db-generate-toc.sh",
)
SCRIPT = os.path.abspath(SCRIPT)


def run_toc(path):
    """Run the TOC script on a directory, return (stdout, stderr, returncode)."""
    r = subprocess.run(
        ["bash", SCRIPT, path],
        capture_output=True,
        text=True,
    )
    return r.stdout, r.stderr, r.returncode


def write_file(directory, name, content):
    """Write a file into directory with given content."""
    path = os.path.join(directory, name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(textwrap.dedent(content))
    return path


class TestReadDescription(unittest.TestCase):
    """Test that read_desc parses various YAML frontmatter styles correctly."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil

        shutil.rmtree(self.tmpdir)

    # ── Single-line styles ───────────────────────────────────────────────

    def test_single_line_unquoted(self):
        write_file(self.tmpdir, "topic.md", """\
            ---
            description: Simple one-line description
            ---
            Body text.
        """)
        out, _, rc = run_toc(self.tmpdir)
        self.assertEqual(rc, 0)
        self.assertIn("Simple one-line description", out)

    def test_single_line_double_quoted(self):
        write_file(self.tmpdir, "topic.md", """\
            ---
            description: "A double-quoted description"
            ---
        """)
        out, _, rc = run_toc(self.tmpdir)
        self.assertEqual(rc, 0)
        self.assertIn("A double-quoted description", out)
        self.assertNotIn('"', out)

    def test_single_line_single_quoted(self):
        write_file(self.tmpdir, "topic.md", """\
            ---
            description: 'A single-quoted description'
            ---
        """)
        out, _, rc = run_toc(self.tmpdir)
        self.assertEqual(rc, 0)
        self.assertIn("A single-quoted description", out)
        self.assertNotIn("'", out)

    # ── Multi-line continuation (indented under key) ─────────────────────

    def test_multiline_continuation(self):
        """The style used by most existing context-db files."""
        write_file(self.tmpdir, "topic.md", """\
            ---
            description:
              How the agent should approach development — git, testing,
              incremental work, logic problems
            ---
        """)
        out, _, rc = run_toc(self.tmpdir)
        self.assertEqual(rc, 0)
        self.assertIn("How the agent should approach development", out)
        self.assertIn("incremental work, logic problems", out)

    def test_multiline_continuation_three_lines(self):
        write_file(self.tmpdir, "topic.md", """\
            ---
            description:
              Line one of description that is quite long and
              continues on line two with more detail and
              finishes on line three
            ---
        """)
        out, _, rc = run_toc(self.tmpdir)
        self.assertEqual(rc, 0)
        self.assertIn("Line one of description", out)
        self.assertIn("finishes on line three", out)

    def test_multiline_quoted(self):
        """Multi-line quoted value (used in some SKILL.md files)."""
        write_file(self.tmpdir, "topic.md", """\
            ---
            description:
              'A quoted multi-line description that spans
              across two lines'
            ---
        """)
        out, _, rc = run_toc(self.tmpdir)
        self.assertEqual(rc, 0)
        self.assertIn("A quoted multi-line description", out)
        self.assertNotIn("'", out)

    # ── YAML block scalar styles (LLM-generated) ────────────────────────

    def test_folded_scalar_gt(self):
        """>  (folded scalar, clip)"""
        write_file(self.tmpdir, "topic.md", """\
            ---
            description: >
              Hook system gotchas and event reference — stdout must be JSON-only,
              exit code semantics, performance traps
            ---
        """)
        out, _, rc = run_toc(self.tmpdir)
        self.assertEqual(rc, 0)
        self.assertIn("Hook system gotchas", out)
        self.assertIn("performance traps", out)

    def test_folded_scalar_gt_strip(self):
        """>-  (folded scalar, strip) — the style that was broken before the fix."""
        write_file(self.tmpdir, "topic.md", """\
            ---
            description: >-
              Hook system gotchas and event reference — stdout must be JSON-only,
              exit code semantics, performance traps
            ---
        """)
        out, _, rc = run_toc(self.tmpdir)
        self.assertEqual(rc, 0)
        self.assertIn("Hook system gotchas", out)
        self.assertIn("performance traps", out)
        # Must NOT contain the literal ">-"
        self.assertNotIn(">-", out)

    def test_literal_scalar_pipe(self):
        """|  (literal scalar, clip)"""
        write_file(self.tmpdir, "topic.md", """\
            ---
            description: |
              A literal block scalar description
              with preserved newlines
            ---
        """)
        out, _, rc = run_toc(self.tmpdir)
        self.assertEqual(rc, 0)
        self.assertIn("A literal block scalar description", out)

    def test_literal_scalar_pipe_strip(self):
        """|-  (literal scalar, strip)"""
        write_file(self.tmpdir, "topic.md", """\
            ---
            description: |-
              A stripped literal scalar description
              that spans multiple lines
            ---
        """)
        out, _, rc = run_toc(self.tmpdir)
        self.assertEqual(rc, 0)
        self.assertIn("A stripped literal scalar description", out)
        self.assertNotIn("|-", out)

    def test_folded_scalar_gt_keep(self):
        """>+  (folded scalar, keep)"""
        write_file(self.tmpdir, "topic.md", """\
            ---
            description: >+
              A keep-mode folded scalar
              with trailing newlines preserved
            ---
        """)
        out, _, rc = run_toc(self.tmpdir)
        self.assertEqual(rc, 0)
        self.assertIn("A keep-mode folded scalar", out)

    def test_literal_scalar_pipe_keep(self):
        """|+  (literal scalar, keep)"""
        write_file(self.tmpdir, "topic.md", """\
            ---
            description: |+
              A keep-mode literal scalar
              with trailing newlines preserved
            ---
        """)
        out, _, rc = run_toc(self.tmpdir)
        self.assertEqual(rc, 0)
        self.assertIn("A keep-mode literal scalar", out)

    # ── Edge cases ───────────────────────────────────────────────────────

    def test_no_frontmatter(self):
        """File without frontmatter should be skipped (no description)."""
        write_file(self.tmpdir, "topic.md", """\
            # Just a heading

            No frontmatter here.
        """)
        out, _, rc = run_toc(self.tmpdir)
        self.assertEqual(rc, 0)
        self.assertNotIn("topic.md", out)

    def test_empty_description(self):
        """Empty description field should be skipped."""
        write_file(self.tmpdir, "topic.md", """\
            ---
            description:
            ---
        """)
        out, _, rc = run_toc(self.tmpdir)
        self.assertEqual(rc, 0)
        self.assertNotIn("topic.md", out)

    def test_description_with_colon(self):
        """Description containing a colon should not confuse the parser."""
        write_file(self.tmpdir, "topic.md", """\
            ---
            description: "Key concept: value-based parsing"
            ---
        """)
        out, _, rc = run_toc(self.tmpdir)
        self.assertEqual(rc, 0)
        self.assertIn("Key concept: value-based parsing", out)

    def test_description_with_special_chars(self):
        """em-dash and other Unicode should pass through."""
        write_file(self.tmpdir, "topic.md", """\
            ---
            description: Architecture overview — design decisions & trade-offs
            ---
        """)
        out, _, rc = run_toc(self.tmpdir)
        self.assertEqual(rc, 0)
        self.assertIn("Architecture overview — design decisions & trade-offs", out)

    def test_other_fields_before_description(self):
        """description is not the first field."""
        write_file(self.tmpdir, "topic.md", """\
            ---
            title: Some Title
            status: draft
            description: The actual description here
            ---
        """)
        out, _, rc = run_toc(self.tmpdir)
        self.assertEqual(rc, 0)
        self.assertIn("The actual description here", out)

    def test_other_fields_after_description(self):
        """Fields after description should not leak into description."""
        write_file(self.tmpdir, "topic.md", """\
            ---
            description: Only this line
            author: someone
            ---
        """)
        out, _, rc = run_toc(self.tmpdir)
        self.assertEqual(rc, 0)
        self.assertIn("Only this line", out)
        self.assertNotIn("someone", out)


class TestTOCStructure(unittest.TestCase):
    """Test TOC output structure — subfolders, files, skipping, status."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil

        shutil.rmtree(self.tmpdir)

    def test_subfolder_listed(self):
        """Subfolder with <name>/<name>.md should appear under ## Subfolders."""
        os.makedirs(os.path.join(self.tmpdir, "hooks"))
        write_file(self.tmpdir, "hooks/hooks.md", """\
            ---
            description: Hook system reference
            ---
        """)
        out, _, rc = run_toc(self.tmpdir)
        self.assertEqual(rc, 0)
        self.assertIn("## Subfolders", out)
        self.assertIn("path: hooks/", out)
        self.assertIn("Hook system reference", out)

    def test_folder_descriptor_skipped_in_files(self):
        """<dirname>.md is the folder descriptor and should NOT appear in ## Files."""
        dirname = os.path.basename(self.tmpdir)
        write_file(self.tmpdir, f"{dirname}.md", """\
            ---
            description: This is the folder descriptor
            ---
        """)
        write_file(self.tmpdir, "real-file.md", """\
            ---
            description: A real file
            ---
        """)
        out, _, rc = run_toc(self.tmpdir)
        self.assertEqual(rc, 0)
        self.assertIn("real-file.md", out)
        self.assertNotIn(f"{dirname}.md", out)

    def test_hidden_files_skipped(self):
        """Files starting with . should be skipped."""
        write_file(self.tmpdir, ".hidden.md", """\
            ---
            description: Should not appear
            ---
        """)
        write_file(self.tmpdir, "visible.md", """\
            ---
            description: Should appear
            ---
        """)
        out, _, rc = run_toc(self.tmpdir)
        self.assertEqual(rc, 0)
        self.assertNotIn(".hidden.md", out)
        self.assertIn("visible.md", out)

    def test_underscore_files_skipped(self):
        """Files starting with _ should be skipped."""
        write_file(self.tmpdir, "_order.md", """\
            ---
            description: Should not appear
            ---
        """)
        write_file(self.tmpdir, "visible.md", """\
            ---
            description: Should appear
            ---
        """)
        out, _, rc = run_toc(self.tmpdir)
        self.assertEqual(rc, 0)
        self.assertNotIn("_order.md", out)
        self.assertIn("visible.md", out)

    def test_status_appended(self):
        """Non-stable status should be appended in brackets."""
        write_file(self.tmpdir, "topic.md", """\
            ---
            description: Work in progress feature
            status: draft
            ---
        """)
        out, _, rc = run_toc(self.tmpdir)
        self.assertEqual(rc, 0)
        self.assertIn("Work in progress feature [draft]", out)

    def test_stable_status_not_appended(self):
        """Stable status should NOT be appended."""
        write_file(self.tmpdir, "topic.md", """\
            ---
            description: A stable feature
            status: stable
            ---
        """)
        out, _, rc = run_toc(self.tmpdir)
        self.assertEqual(rc, 0)
        self.assertIn("A stable feature", out)
        self.assertNotIn("[stable]", out)

    def test_multiple_files_sorted(self):
        """Multiple files should all appear in output."""
        write_file(self.tmpdir, "alpha.md", """\
            ---
            description: Alpha topic
            ---
        """)
        write_file(self.tmpdir, "beta.md", """\
            ---
            description: Beta topic
            ---
        """)
        write_file(self.tmpdir, "gamma.md", """\
            ---
            description: Gamma topic
            ---
        """)
        out, _, rc = run_toc(self.tmpdir)
        self.assertEqual(rc, 0)
        self.assertIn("alpha.md", out)
        self.assertIn("beta.md", out)
        self.assertIn("gamma.md", out)

    def test_mixed_subfolders_and_files(self):
        """Both sections appear when both exist."""
        os.makedirs(os.path.join(self.tmpdir, "sub"))
        write_file(self.tmpdir, "sub/sub.md", """\
            ---
            description: A subfolder
            ---
        """)
        write_file(self.tmpdir, "file.md", """\
            ---
            description: A file
            ---
        """)
        out, _, rc = run_toc(self.tmpdir)
        self.assertEqual(rc, 0)
        self.assertIn("## Subfolders", out)
        self.assertIn("## Files", out)
        self.assertIn("path: sub/", out)
        self.assertIn("path: file.md", out)

    def test_empty_directory(self):
        """Empty directory produces no output and exits 0."""
        out, _, rc = run_toc(self.tmpdir)
        self.assertEqual(rc, 0)
        self.assertEqual(out.strip(), "")

    def test_nonexistent_directory(self):
        """Non-existent directory should error."""
        out, err, rc = run_toc("/tmp/nonexistent_dir_xyz_12345")
        self.assertNotEqual(rc, 0)
        self.assertIn("not a directory", err)

    def test_subfolder_no_descriptor(self):
        """Subfolder without <name>.md should not appear."""
        os.makedirs(os.path.join(self.tmpdir, "orphan"))
        write_file(self.tmpdir, "orphan/something.md", """\
            ---
            description: Some file in orphan folder
            ---
        """)
        out, _, rc = run_toc(self.tmpdir)
        self.assertEqual(rc, 0)
        self.assertNotIn("orphan/", out)

    def test_subfolder_status_appended(self):
        """Subfolder with non-stable status gets it appended."""
        os.makedirs(os.path.join(self.tmpdir, "wip"))
        write_file(self.tmpdir, "wip/wip.md", """\
            ---
            description: Work in progress section
            status: wip
            ---
        """)
        out, _, rc = run_toc(self.tmpdir)
        self.assertEqual(rc, 0)
        self.assertIn("Work in progress section [wip]", out)

    def test_subfolder_missing_description(self):
        """Subfolder descriptor with no description gets '(no description)'."""
        os.makedirs(os.path.join(self.tmpdir, "empty"))
        write_file(self.tmpdir, "empty/empty.md", """\
            ---
            status: draft
            ---
        """)
        out, _, rc = run_toc(self.tmpdir)
        self.assertEqual(rc, 0)
        self.assertIn("(no description)", out)
        self.assertIn("path: empty/", out)


class TestBlockScalarRegression(unittest.TestCase):
    """
    Regression tests for the >- fix.

    These mirror real-world frontmatter an LLM might generate. Each test
    verifies the description is extracted correctly, not returned as the
    literal indicator string.
    """

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil

        shutil.rmtree(self.tmpdir)

    def test_gt_strip_real_world(self):
        """Real example from the bug report."""
        write_file(self.tmpdir, "hooks.md", """\
            ---
            description: >-
              Hook system gotchas and event reference — stdout must be JSON-only, exit code
              semantics, event flow-control capabilities, union aggregation, tail calls,
              performance traps
            ---
        """)
        out, _, rc = run_toc(self.tmpdir)
        self.assertEqual(rc, 0)
        self.assertIn("Hook system gotchas", out)
        self.assertIn("performance traps", out)
        self.assertNotIn(">-", out)

    def test_gt_strip_single_continuation_line(self):
        """>- with only one continuation line."""
        write_file(self.tmpdir, "topic.md", """\
            ---
            description: >-
              Just one continuation line here
            ---
        """)
        out, _, rc = run_toc(self.tmpdir)
        self.assertEqual(rc, 0)
        self.assertIn("Just one continuation line here", out)

    def test_pipe_strip_real_world(self):
        """|- with multi-line content."""
        write_file(self.tmpdir, "topic.md", """\
            ---
            description: |-
              Config file reference — location, format,
              supported keys, and reload behavior
            ---
        """)
        out, _, rc = run_toc(self.tmpdir)
        self.assertEqual(rc, 0)
        self.assertIn("Config file reference", out)
        self.assertIn("reload behavior", out)

    def test_gt_with_explicit_indent_indicator(self):
        """>2 — folded with explicit indent indicator."""
        write_file(self.tmpdir, "topic.md", """\
            ---
            description: >2
              An indented folded scalar with explicit indent
              spanning two lines
            ---
        """)
        out, _, rc = run_toc(self.tmpdir)
        # This is an edge case — >2 may or may not be handled.
        # At minimum it should not crash.
        self.assertEqual(rc, 0)

    def test_all_block_indicators_no_crash(self):
        """Every block scalar indicator variant should not crash the script."""
        indicators = [">", ">-", ">+", "|", "|-", "|+"]
        for i, indicator in enumerate(indicators):
            write_file(self.tmpdir, f"topic{i}.md", f"""\
---
description: {indicator}
  Content for {indicator} test
---
""")
        out, _, rc = run_toc(self.tmpdir)
        self.assertEqual(rc, 0)
        for indicator in indicators:
            with self.subTest(indicator=indicator):
                self.assertIn(f"Content for {indicator} test", out)


if __name__ == "__main__":
    unittest.main()
