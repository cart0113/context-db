---
type: Decision
description:
  Why all scripts are Python 3 with argparse — minimal dependency choice, why
  not bash, why not click
---

# Python and Argparse

The skill is one Python 3 script, stdlib only, with argparse for CLI parsing. It
targets Python 3.8 so it runs on old system interpreters.

## Why Python 3

- **Near-zero dependency.** Python 3 ships on macOS and virtually all Linux
  distros. No pip install, no venv, no package management.
- **Better than bash for this task.** The scripts parse YAML frontmatter, walk
  directory trees, handle symlinks, and compose template text. Bash + awk could
  do this (and the original TOC script did), but the Python versions are more
  readable, testable, and maintainable. The bash version required careful
  avoidance of bash 4+ features for macOS 3.2 compatibility.
- **Testable.** The script is covered by `tests/`. The bash version had none.
- **No PyYAML.** Frontmatter is read by a small hand-rolled parser that handles
  only top-level scalar keys. Do not replace it with a YAML dependency.

## Why argparse over click

Click is a better CLI library, but it's a third-party dependency. Argparse ships
with Python 3. The goal is zero external dependencies — the skill should work on
any machine with Python 3, no setup required.
