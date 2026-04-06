# Reference

## Description files

A folder is a **context node** if it contains any of these files:

- `<folder_name>.md`
- `<folder_name>-instructions.md`
- `CONTEXT.md`, `SKILL.md`, `AGENT.md`, or `AGENTS.md`

The file has YAML frontmatter with a single `description` key. No body content.

```yaml
---
description: Acme Payments — architecture, APIs, and data model
---
```

## Context documents

Individual `.md` files with YAML frontmatter and content. The `description`
appears in the parent's TOC when `show_toc.sh` is run.

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

When `status` is not `stable`, `show_toc.sh` appends it to the TOC entry so
agents see it without opening the file.

## Directory structure

```
your-project/
├── bin/show_toc.sh                      ← TOC generator
└── context-db/
    ├── context-db-instructions.md       ← reading/writing rules
    ├── project-name/
    │   ├── project-name.md              ← folder description
    │   ├── architecture.md              ← context document
    │   └── data-model/                  ← nested subfolder
    │       ├── data-model.md
    │       └── entities.md
    └── shared/                          ← symlinked folder
        └── coding-standards/
            └── coding-standards.md
```

## Symlinks

Symlinked folders appear in the TOC when `show_toc.sh` is run on the parent. The
script resolves symlinks to find the real folder name for description file
lookup, so symlinks can be named freely.

## Skipping

Underscore-prefixed (`_drafts/`) and dot-prefixed (`.hidden/`) names are always
skipped.

## TOC format

`show_toc.sh` prints the TOC to stdout in this format:

<!-- prettier-ignore -->
```markdown
## Subfolders

- description: Database schema, entities, and relationships
  path: data-model/data-model-toc.md

## Files

- description: REST API endpoints, authentication, and error codes
  path: api-reference.md
- description: System components, data flow, and service boundaries
  path: architecture.md
```

Each entry has `description:` on the first line and `path:` on the second.
Sections only appear when there are entries. An empty folder produces no output.

## show_toc.sh

Generates a TOC for a context-db folder and prints it to stdout.

```bash
bin/show_toc.sh context-db/                     # Top-level TOC
bin/show_toc.sh context-db/my-project/          # Subfolder TOC
bin/show_toc.sh context-db/my-project/data-model/  # Deeper
```

- Takes a single directory argument
- Finds the description file for that directory
- Lists subfolders (that are context nodes) and files with their descriptions
- Resolves symlinks for description file lookup but follows them for reading
- Skips underscore-prefixed and dot-prefixed names
- Requires bash 3.2+, awk (standard on macOS and Linux)

## build_toc.sh (legacy)

Generates static `<folder>-toc.md` files on disk. Retained for projects that
need files on disk (static site generation, non-agent consumers). For agent
navigation, `show_toc.sh` is preferred — it avoids committing generated files
and handles cross-project symlinks cleanly.

```bash
bin/build_toc.sh                    # Rebuild changed TOC files
bin/build_toc.sh context-db/        # Build one directory tree
bin/build_toc.sh --build-all        # Rebuild all TOC files unconditionally
```

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
