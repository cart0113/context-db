# Specification

## Description File

A folder is a context node if it contains any of: `<folder_name>.md`, `<folder_name>-instructions.md`, `CONTEXT.md`, `SKILL.md`, `AGENT.md`, or `AGENTS.md`. The file should only have YAML front matter with a single `description` key. Other content is ignored and should not be included.

```markdown
---
description: Acme Payments — architecture, APIs, and data model
---
```

## Context Documents

Individual `.md` files with YAML front matter and content. The description appears in the parent's `-toc.md`.

```markdown
---
description: System components, data flow, and service boundaries
---

# Architecture

(content)
```

## TOC Generation

`bin/build_toc.sh` walks the directory tree and generates `<folder>-toc.md` for each context node. By default it only rebuilds when source files are newer than the existing TOC. Use `--build-all` to force a full rebuild.

## Symlinks

Symlinked folders appear in the parent's TOC. The script never writes into a folder whose real path is outside the project root.

## Skipping

Underscore-prefixed (`_drafts/`) and dot-prefixed (`.hidden/`) names are always skipped.

## Change Detection

The script compares file modification times. A TOC is rebuilt when any of these are newer:
- The description file
- Any `.md` file in the directory
- Any description file in a subdirectory
