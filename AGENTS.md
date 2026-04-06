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

## context-db

Read `context-db/context-db-instructions.md` — it contains all rules for
reading, writing, and maintaining the project knowledge database.
