# AGENTS.md

This file provides guidance to AI assistants when working with code in this
repository.

## CRITICAL: Read Global User Context First

**BEFORE PROCEEDING, read `~/.context.md` and follow all advice there.** That
file contains general coding preferences, style guidelines, and critical
instructions that apply to ALL projects.

If ~/.context.md doesn't exist, notify the user.

## Project Overview

**context-db** — hierarchical Markdown knowledge base with on-demand TOCs for
LLM agents. Agents run `bin/show_toc.sh`, browse descriptions, fetch what's
relevant, and write back what they learn.

## Code Structure

```
bin/show_toc.sh       On-demand TOC generator (bash 3.2+)
context-db/           This project's own knowledge database
templates/            Ready-to-copy files for new projects
example/              Example project structure
docs/                 GitHub Pages documentation (bruha)
hooks/pre-commit      Git hook for formatting
```

## Language

Bash project. The core script (`bin/show_toc.sh`) targets bash 3.2+.

## context-db

Read `context-db/context-db-instructions.md` — it contains all rules for
reading, writing, and maintaining the project knowledge database.
