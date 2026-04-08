---
description:
  Why context-db-generate-toc.sh is pure bash rather than Python or another
  language
---

# Bash Over Python

The scripts are written in bash (3.2+) with awk for parsing.

## Rationale

- **Zero dependencies.** Every Unix system (macOS, Linux, WSL) has bash and awk
  pre-installed. No Python version management, no `pip install`, no venv.
- **macOS compatibility.** macOS ships bash 3.2 (GPLv2). The script avoids bash
  4+ features: no associative arrays (`declare -A`), no namerefs (`local -n`),
  no `readarray`. This was validated the hard way during initial development.
- **The task is small.** The script parses YAML-like blocks, scans directories,
  and writes Markdown. This is squarely in bash's sweet spot. A Python rewrite
  would add complexity (argparse, pathlib, YAML library) for no functional
  benefit.
- **Git hook friendly.** Pre-commit hooks that shell out to Python are slower to
  start and require the right Python to be on PATH. Bash hooks run instantly.
