---
description:
  Why static -toc.md files were replaced with a script that generates TOC on
  stdout — solves the cross-project symlink problem
---

# Dynamic TOC Generation

Static, committed `-toc.md` files were replaced with
`context-db-generate-toc.py`, a script that generates the TOC for any context-db
folder on the fly and prints it to stdout.

## Problem

Static `-toc.md` files broke down with cross-project sharing:

1. You symlink external context into `context-db/` and `.gitignore` the symlink
2. The parent TOC gets regenerated to include the symlinked folder
3. Now the committed TOC either includes entries only you have (broken for
   others) or excludes entries you have (your agent misses them)

There is no clean way to have a committed file reflect per-user symlinks.

## Solution

The TOC script takes a context-db folder path and prints the TOC to stdout. No
files written, nothing to commit. The agent runs it on the root, then
recursively on subfolders as it navigates deeper.

This works with every major agent framework — Claude Code (Bash tool), Cursor
(Terminal tool), MCP servers, custom agents. A script that returns text on
stdout is the simplest possible interface.
