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
knowledge as Markdown files, with on-demand tables of contents for progressive
disclosure.

An agent runs `bin/show_toc.sh` on a folder, sees one-line descriptions of every
subfolder and file, and fetches only what's relevant to the current task.

## Code Structure

```
bin/show_toc.sh       # On-demand TOC generator (prints to stdout)
hooks/pre-commit      # Git hook for formatting
context-db/           # This project's own context knowledge database
templates/            # Tool-specific bootstrap templates
example/              # Example project structure
docs/                 # GitHub Pages documentation
```

## Language

This is a **bash** project. The core script (`bin/show_toc.sh`) targets bash
3.2+.

## context-db — IMPORTANT: Read AND Write

Read `context-db/context-db-instructions.md` for the project knowledge database.

**You are expected to update the context-db when you learn something
important.** When you discover architecture decisions, non-obvious patterns,
constraints, gotchas, data model relationships, or anything a future agent would
need to work safely on this codebase — add it to the context-db. If you had to
figure it out the hard way, it belongs there.

**CRITICAL: Always maintain frontmatter.** Every file and folder description in
context-db has YAML frontmatter with a `description` field. When you create or
modify any context-db content, you MUST ensure the `description` accurately
reflects the current content. Stale descriptions mislead future agents. See
`context-db-instructions.md` for the full rules.
