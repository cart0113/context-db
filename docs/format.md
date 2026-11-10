# Format

A context-db bundle is a conformant
[Open Knowledge Format v0.2](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md)
bundle: a directory of Markdown files with YAML frontmatter. context-db uses a
small, stable subset of OKF and adds a few conventions of its own.

## Layout

```text
context-db/                         a mount point, not itself a bundle
├── context-db.json
├── context-db.local.json           optional, gitignored
├── context-db-on-markdown/         ON_*.md files
├── <name>-project/                 the project bundle
└── <anything else>/                background bundles
```

Each top-level folder is its own bundle. The config and ON files sit outside
every bundle, so they need no frontmatter.

## What the agent is told

This is the format reference the `update` and `wip` commands print:

```{literalinclude} ../skill/context-db/prompts/format.md
:language: markdown
```

## A file

```markdown
---
type: Decision
description:
  Why refunds are processed asynchronously, and the idempotency-key rule that
  follows from it
---

# Asynchronous refunds

...
```

## An index

`index.md` is generated from frontmatter by the `index` helper:

```markdown
---
okf_version: "0.2"
---

# Subfolders

* [data-model](data-model/index.md) - Database schema, entities, and relationships
* [wip](wip/index.md) - Current work in progress

# Files

* [Architecture](architecture.md) - System components, data flow, and service boundaries
```

Only a bundle's root index carries `okf_version`. Link text is the file's
`title` key if it has one, else its first H1, else its filename. A status other
than `stable` is appended in brackets.

## How this maps to OKF

| OKF v0.2                           | context-db                                             |
| ---------------------------------- | ------------------------------------------------------ |
| `type` required                    | Required, from a suggested vocabulary                  |
| `description` recommended          | Required                                               |
| `index.md` optional                | Always generated                                       |
| `status`: draft, stable, deprecated | Same                                                  |
| Links bundle-relative or relative  | File-relative only                                     |
| `log.md` optional                  | Not used; git history is the log                       |
| `title`, `tags`                    | Not written; tolerated                                 |
| `generated`, `verified`, `sources`, `stale_after` | Not written; tolerated                  |
| Attested computations              | Not used                                               |

Three conventions go beyond OKF:

- **Folder descriptors.** `<folder>/<folder>.md` with `type: Folder` holds the
  folder's description. To OKF it is an ordinary concept.
- **`wip/`.** A folder in the project bundle for plans that are deleted when the
  work lands. Its files may carry a `branch` key.
- **Symlinks only at the top level.** A symlink inside a bundle is a lint error.

### Why some of OKF is left out

The trust and provenance keys duplicate what `git blame` and `git log` already
record for a bundle that lives in a repository, and a trust field nobody
maintains is worse than none. Bundle-relative links (`/x.md`) resolve against
the repository root on GitHub and in most Markdown tools, so they break whenever
a bundle is a subdirectory.

OKF is young: v0.1 and v0.2 were six weeks apart and a v0.3 is in development.
context-db depends only on the parts that have not changed since v0.1.

## Lint

`index` reports these as errors:

- a file with no frontmatter, no `type`, or no `description`
- a `status` other than `draft`, `stable`, or `deprecated`
- a broken relative link, or a link starting with `/`
- a folder with no descriptor
- a symlink inside a bundle

And these as warnings: a file over 200 lines outside `wip/`, and a folder with
more than 12 items.
