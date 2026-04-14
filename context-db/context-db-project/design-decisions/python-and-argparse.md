---
description:
  Why all scripts are Python 3 with argparse — minimal dependency choice, why
  not bash, why not click
---

# Python and Argparse

All context-db scripts (TOC generation, main-agent dispatcher, sub-agent
spawner) are Python 3 with argparse for CLI parsing.

## Why Python 3

- **Near-zero dependency.** Python 3 ships on macOS and virtually all Linux
  distros. No pip install, no venv, no package management.
- **Better than bash for this task.** The scripts parse YAML frontmatter, walk
  directory trees, handle symlinks, and compose template text. Bash + awk could
  do this (and the original TOC script did), but the Python versions are more
  readable, testable, and maintainable. The bash version required careful
  avoidance of bash 4+ features for macOS 3.2 compatibility.
- **Testable.** The Python TOC script has 72 tests. The bash version had none.

## Why argparse over click

Click is a better CLI library, but it's a third-party dependency. Argparse ships
with Python 3. The goal is zero external dependencies — the skill should work on
any machine with Python 3, no setup required.
