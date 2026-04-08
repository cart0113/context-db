# Reference

## Description files

A folder is a **context node** if it contains any of these files:

- `<folder_name>.md`
- `<folder_name>-instructions.md`
- `CONTEXT.md`, `SKILL.md`, `AGENT.md`, or `AGENTS.md`

The file has YAML frontmatter with a `description` key. No body content.

```yaml
---
description: Acme Payments — architecture, APIs, and data model
---
```

Descriptions can span multiple lines using YAML block scalar syntax:

```yaml
---
description:
  Acme Payments — architecture, APIs, data model, and deployment constraints
---
```

## Context documents

Individual `.md` files with YAML frontmatter and content. The `description`
appears in the parent's TOC when `context-db-generate-toc.sh` is run.

```yaml
---
description: System components, data flow, and service boundaries
---
# Architecture

(content)
```

## Optional fields

The only required field is `description`.

### status

Lifecycle stage of the document: `draft`, `stable`, or `deprecated`. Default
(when omitted): `stable`.

```yaml
---
description: Legacy payment processing flow
status: deprecated
---
```

When `status` is not `stable`, `context-db-generate-toc.sh` appends it to the
TOC entry so agents see it without opening the file.

## Directory structure

```
your-project/
├── .claude/                                       ← Claude Code; .cursor/ for Cursor, .agents/ for Codex
│   ├── rules/context-db.md                        ← rule: load the skill
│   └── skills/context-db/                         ← skill: instructions + script
│       ├── SKILL.md
│       └── scripts/context-db-generate-toc.sh
└── context-db/
    ├── project-name-project/                      ← main project context
    │   ├── project-name-project.md                ← folder description
    │   ├── architecture.md                        ← context document
    │   └── data-model/                            ← nested subfolder
    │       ├── data-model.md
    │       └── entities.md
    └── coding-standards/                          ← ancillary (symlinked)
        └── coding-standards.md
```

## Symlinks

Symlinked folders appear in the TOC when `context-db-generate-toc.sh` is run on
the parent. The script resolves symlinks to find the real folder name for
description file lookup, so symlinks can be named freely.

To keep a symlink private (visible only to you), add it to `.gitignore`:

```gitignore
context-db/my-private-link
```

Because `context-db-generate-toc.sh` generates the TOC on the fly, private
symlinks appear in your TOC automatically without affecting anyone else's
working tree. See the [Cross-Project Sharing](../guide/cross-project-sharing.md)
guide for patterns.

## Skipping

Underscore-prefixed (`_drafts/`) and dot-prefixed (`.hidden/`) names are always
skipped.

## TOC format

`context-db-generate-toc.sh` prints the TOC to stdout in this format:

<!-- prettier-ignore -->
```markdown
## Subfolders

- description: Database schema, entities, and relationships
  path: data-model/

## Files

- description: REST API endpoints, authentication, and error codes
  path: api-reference.md
- description: System components, data flow, and service boundaries
  path: architecture.md
```

Each entry has `description:` on the first line and `path:` on the second.
Sections only appear when there are entries. An empty folder produces no output.

## context-db-generate-toc.sh

Generates a TOC for a context-db folder and prints it to stdout.

```bash
.claude/skills/context-db/scripts/context-db-generate-toc.sh context-db/
.claude/skills/context-db/scripts/context-db-generate-toc.sh context-db/my-project/
.claude/skills/context-db/scripts/context-db-generate-toc.sh context-db/my-project/data-model/
```

- Takes a single directory argument.
- Finds the description file for that directory.
- Lists subfolders (that are context nodes) and files with their descriptions.
- Resolves symlinks for description file lookup but follows them for reading.
- Skips underscore-prefixed and dot-prefixed names.
- Requires bash 3.2+, awk (standard on macOS and Linux).

## build_site.sh

Generates a browsable Docsify site from a context-db directory.

```bash
bin/build_site.sh <source_dir> <output_dir>
bin/build_site.sh --embed <source_dir> <output_dir>
bin/build_site.sh --template file.html <source_dir> <output_dir>
```

| Flag         | Effect                                                           |
| ------------ | ---------------------------------------------------------------- |
| `--embed`    | Skip index.html / .nojekyll (for nesting under existing Docsify) |
| `--template` | Use a custom index.html instead of the default                   |

## pre-commit hook

Runs formatters (prettier, ruff) on staged files:

```bash
cp hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```
