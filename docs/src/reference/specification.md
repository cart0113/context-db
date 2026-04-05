# Specification

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
appears in the parent's `-toc.md`.

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

When `status` is not `stable`, `build_toc.sh` appends it to the TOC entry so
agents see it without opening the file. A `deprecated` document should not be
trusted for current behavior. A `draft` document is tentative and may be
incomplete.

## Directory structure

A typical project:

```
your-project/
└── context-db/
    ├── context-db-instructions.md       ← reading/writing rules
    ├── context-db-toc.md                ← generated
    ├── project-name/
    │   ├── project-name.md              ← folder description
    │   ├── project-name-toc.md          ← generated
    │   ├── architecture.md              ← context document
    │   ├── api-reference.md
    │   └── data-model/                  ← nested subfolder
    │       ├── data-model.md
    │       ├── data-model-toc.md
    │       ├── entities.md
    │       └── schema-conventions.md
    └── shared/                          ← symlinked folder
        └── coding-standards/
            ├── coding-standards.md
            └── coding-standards-toc.md
```

## TOC generation

`bin/build_toc.sh` walks the directory tree and generates `<folder>-toc.md` for
each context node. By default it only rebuilds when source files are newer than
the existing TOC. Use `--build-all` to force a full rebuild.

## Symlinks

Symlinked folders appear in the parent's TOC. The script reads descriptions from
symlinked folders but never writes into a folder whose real path is outside the
project root.

## Skipping

Underscore-prefixed (`_drafts/`) and dot-prefixed (`.hidden/`) names are always
skipped.

## Change detection

A TOC is rebuilt when any of these are newer than the existing `-toc.md`:

- The description file
- Any `.md` file in the directory
- Any description file in a subdirectory
