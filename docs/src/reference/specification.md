# Reference

## Description files

A folder is a **context node** if it contains a descriptor file:

- `<folder_name>.md`
- `<folder_name>-instructions.md`
- `CONTEXT.md`, `SKILL.md`, `AGENT.md`, or `AGENTS.md`

The descriptor has YAML frontmatter with a `description` key and an empty body.

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

The descriptor for the **project folder** should open with the marker
`Main project folder for this repo.` — the dispatcher and `maintain` command
rely on it to distinguish the project folder from parallel external folders.

```yaml
---
description:
  Main project folder for this repo. Acme Payments — architecture, APIs, data
  model.
---
```

## Context documents

Individual `.md` files with YAML frontmatter and body. The `description` appears
in the parent's TOC when the TOC script is run.

```yaml
---
description: System components, data flow, and service boundaries
---
# Architecture

(content)
```

## Optional fields

The only required frontmatter field is `description`.

### `status`

Lifecycle stage of the document: `draft`, `stable`, or `deprecated`. Default
(when omitted): `stable`.

```yaml
---
description: Legacy payment processing flow
status: deprecated
---
```

When `status` is not `stable`, the TOC script appends it to the entry so agents
see the lifecycle without opening the file.

## The `ON_*.md` special files

Three optional files at the **root** of `context-db/` are inlined automatically
when their command runs. They are the only always-on mechanism — there is no
configuration file and no glob list.

| File                        | Inlined on                   |
| --------------------------- | ---------------------------- |
| `context-db/ON_PROMPT.md`   | every `/context-db prompt`   |
| `context-db/ON_UPDATE.md`   | every `/context-db update`   |
| `context-db/ON_MAINTAIN.md` | every `/context-db maintain` |

Rules:

- Presence is the only switch. If the file exists, it is used; if not, nothing
  happens.
- The body is inlined raw — frontmatter stripped, no preamble, no path
  attribution, no headings added. Whatever the file contains is what the agent
  sees. The author owns the framing.
- Give each file YAML `description` frontmatter so it appears in the TOC when
  the script runs on the `context-db/` root. The frontmatter is stripped on
  inline, so it costs nothing at run time.
- The content is placed right before the user's instruction (for `prompt` and
  `update`) or at the end of the output (for `maintain`). Recency matters: it is
  the freshest thing in the agent's context when it acts.

In practice `ON_PROMPT.md` is the only one most projects use; `ON_UPDATE.md` and
`ON_MAINTAIN.md` exist for the rare case. A worked example to copy lives at
`templates/ON_PROMPT.md`.

## Directory layout

```
your-project/
├── AGENTS.md                              ← opt-in standing instructions
├── .claude/
│   └── skills/context-db/                 ← the skill: dispatcher + scripts
│       ├── SKILL.md
│       └── scripts/
│           ├── context-db-generate-toc.py
│           ├── context-db-main-agent.py
│           └── context-db-resolve-path.py
└── context-db/
    ├── ON_PROMPT.md                       ← optional, inlined on every prompt
    ├── ON_UPDATE.md                       ← optional, inlined on every update
    ├── ON_MAINTAIN.md                     ← optional, inlined on every maintain
    ├── <project-name>-project/            ← knowledge specific to this repo
    │   ├── <project-name>-project.md      ← folder descriptor
    │   ├── architecture.md                ← context document
    │   └── data-model/
    │       ├── data-model.md
    │       └── entities.md
    └── coding-standards/                  ← project-agnostic, often symlinked
```

## Symlinks

Symlinked folders appear in the TOC when the script runs on the parent. The
script resolves symlinks to find the real folder name for descriptor lookup, so
symlinks can be named freely. Cross-references that traverse symlinked subtrees
should use the path-resolver script:

```bash
python3 .claude/skills/context-db/scripts/context-db-resolve-path.py \
  <containing-file> <link>
```

It prints an absolute path that resolves correctly through the symlink. Direct
`..` traversal is unreliable inside a symlinked tree.

To keep a symlink private, add it to `.gitignore`:

```gitignore
context-db/my-private-link
```

The TOC is generated on the fly, so private symlinks appear in your TOC without
affecting anyone else's working tree. See
[Cross-Project Sharing](../guide/cross-project-sharing.md).

## Skipping

Underscore-prefixed (`_drafts/`) and dot-prefixed (`.hidden/`) names are always
skipped.

## TOC format

`context-db-generate-toc.py` prints to stdout in this format:

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

## Scripts

### `context-db-generate-toc.py`

Generates a TOC for a context-db folder and prints it to stdout.

```bash
python3 .claude/skills/context-db/scripts/context-db-generate-toc.py context-db/
python3 .claude/skills/context-db/scripts/context-db-generate-toc.py context-db/my-project/
```

- Single directory argument.
- Finds the descriptor file for that directory.
- Lists subfolders (that are context nodes) and files with descriptions.
- Resolves symlinks for descriptor lookup but follows them for reading.
- Skips underscore-prefixed and dot-prefixed names.
- Pure Python 3 — no third-party dependencies.

### `context-db-main-agent.py`

The command dispatcher. See [Commands](../guide/commands.md) for the catalog and
[CLI reference](cli.md) for the literal `--help` and instruction text.

```bash
python3 .claude/skills/context-db/scripts/context-db-main-agent.py <command> [args]
```

Commands: `prompt`, `update`, `maintain`, `read`, `help`. Where a command takes
an instruction it is one positional argument — multi-word instructions must be
quoted as a single shell argument.

### `context-db-resolve-path.py`

Resolves cross-reference paths inside symlinked subtrees. Prints an absolute
path to stdout.

```bash
python3 .claude/skills/context-db/scripts/context-db-resolve-path.py \
  <containing-file> <link>
```

## `build_site.sh`

Generates a browsable Docsify site from a context-db directory.

```bash
bin/build_site.sh <source_dir> <output_dir>
bin/build_site.sh --embed <source_dir> <output_dir>
bin/build_site.sh --template file.html <source_dir> <output_dir>
```

| Flag         | Effect                                                                |
| ------------ | --------------------------------------------------------------------- |
| `--embed`    | Skip `index.html` / `.nojekyll` (for nesting under existing Docsify). |
| `--template` | Use a custom `index.html` instead of the default.                     |

## pre-commit hook

Runs formatters (prettier, ruff) on staged files and regenerates the CLI
reference when the dispatcher or prompt templates change:

```bash
cp hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```
