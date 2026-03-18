# Quick Start

## 1. Add a CONTEXT/ directory to your project

```
your_project/
└── CONTEXT/
    ├── CONTEXT.yml
    ├── CONTEXT_MD_SYSTEM_INSTRUCTIONS.md
    └── CONTEXT_TOC.md                     (will be generated)
```

You can copy the example structure to get started:

```bash
cp -r path/to/context-md/examples/my_project/CONTEXT your_project/CONTEXT
```

## 2. Edit CONTEXT.yml

`CONTEXT.yml` is the config file for this context node. Edit the `title`, `description`,
and any indexing options:

```yaml
title: My Project Context
description: Context for my_project — architecture and coding conventions

depth: 1
skip_underscore: true
ignore: []
read_only: []
eager_read: []
```

| Field | Default | Description |
|-------|---------|-------------|
| `title` | (untitled) | Name shown as heading in the generated TOC |
| `description` | (empty) | One-line summary shown in parent TOC entries |
| `depth` | `1` | Discovery depth (1 = direct children only) |
| `skip_underscore` | `true` | Ignore files/folders whose names start with `_` |
| `ignore` | `[]` | Files/folders to exclude from the TOC |
| `read_only` | `[]` | Include in TOC but don't rebuild (for symlinked external resources) |
| `eager_read` | `[]` | Folders the LLM should always load when reading this TOC |

## 3. Write context documents

Add `.md` files to `CONTEXT/`. Each file should have YAML front matter with `title`
and `description` — these are what appear in the auto-generated TOC:

```markdown
---
title: Architecture Overview
description: High-level description of system components and their relationships
---

# Architecture Overview

...
```

## 4. Build the TOC

```bash
# From project root — finds and builds all CONTEXT_TOC.md files
bin/build_toc.sh

# Or build a specific directory
bin/build_toc.sh your_project/CONTEXT/
```

This generates `CONTEXT_TOC.md` completely. Do not edit it by hand.

## 5. Wire up automatic rebuilds

Copy the pre-commit hook so TOCs stay current with every commit:

```bash
cp hooks/pre-commit your_project/.git/hooks/pre-commit
chmod +x your_project/.git/hooks/pre-commit
```

## 6. Wire up the agent entry point

The `CONTEXT_MD_SYSTEM_INSTRUCTIONS.md` file is only useful if agents know to read it.
Choose one:

**As a skill** (Claude Code, Codex, etc.):
```bash
ln -s /path/to/context-md/skills/context-md.md your_project/skills/context-md.md
```

**As a Cursor rule:**
```bash
mkdir -p your_project/.cursor/rules
cp /path/to/context-md/templates/cursor-rule.mdc your_project/.cursor/rules/context-md.mdc
```

Copy the template and customize the "About This Project" section for your codebase.

## Organizing subfolders

For large projects, group related context into subfolders. Each subfolder gets its
own `CONTEXT.yml` and `CONTEXT_TOC.md`:

```
CONTEXT/
├── CONTEXT.yml
├── CONTEXT_TOC.md
├── architecture.md
└── CODING_STYLE/
    ├── CONTEXT.yml          ← description appears in parent's Subfolders table
    ├── CONTEXT_TOC.md
    └── defensive_coding.md
```

## Sharing context across projects

Because any `CONTEXT/` subfolder is self-contained, it can be a symlink:

```bash
# In your project
ln -s /shared/CODING_STYLE_CONTEXT CONTEXT/CODING_STYLE

# If the linked folder is externally managed, mark it read_only in CONTEXT.yml
# so build_toc.sh won't attempt to rebuild it:
#   read_only: [CODING_STYLE]
```
