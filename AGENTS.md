# AGENTS.md

This file provides guidance to AI assistants when working with code in this
repository.

## CRITICAL: Read Global User Context First

**BEFORE PROCEEDING, read `~/.context.md` and follow all advice there.** That
file contains my general coding preferences, style guidelines, and critical
instructions that apply to ALL projects. The instructions in ~/.context.md
override any conflicting defaults.

If ~/.context.md doesn't exist, notify the user.

## Project Overview

**context-db** is a portable standard for hierarchically organizing project
knowledge as Markdown files, with auto-generated tables of contents for
progressive disclosure.

An LLM reads a lightweight `-toc.md` index, sees one-line descriptions of every
subfolder and file, and fetches only what's relevant to the current task.

## Code Structure

```
bin/build_toc.sh      # TOC generator script
hooks/pre-commit      # Git hook for auto-rebuild
context-db/           # This project's own context knowledge database
templates/            # Tool-specific bootstrap templates
example/              # Example project structure
docs/                 # GitHub Pages documentation
```

## Language

This is a **bash** project. The core script (`bin/build_toc.sh`) targets bash
3.2+.

## context-db — IMPORTANT: Read AND Write

Read `context-db/context-db-instructions.md` for the project knowledge database.

**You are expected to update the context-db when you learn something
important.** When you discover architecture decisions, non-obvious patterns,
constraints, gotchas, data model relationships, or anything a future agent would
need to work safely on this codebase — add it to the context-db. If you had to
figure it out the hard way, it belongs there. Update descriptions in frontmatter
to stay accurate. Flag or remove stale content that contradicts the current
code.
