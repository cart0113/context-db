# Migrating from v0.0

Version 0.1 is a rewrite. The idea is the same and the layout is different.

## What changed

| v0.0 | v0.1 |
| --- | --- |
| Frontmatter has `description` | Frontmatter has `type` and `description`, as OKF requires |
| A script prints the table of contents | Every folder has a generated `index.md` that the agent reads |
| Commands: `prompt`, `update`, `maintain`, `read` | Commands: `prompt`, `update`, `wip`, `configure` |
| No settings | `context-db.json`, with optional `context-db.local.json` |
| `context-db/ON_PROMPT.md` | `context-db/context-db-on-markdown/ON_PROMPT.md` |
| `<name>-project/wip.md` | `<name>-project/wip/` folder |
| Paths in backticks, and a script to resolve them | Markdown links |
| Three scripts | One script |

## How to migrate

A script does the mechanical part. It adds a guessed `type` to every file, turns
backticked paths into links, and moves the `ON_*.md` files and `wip.md`. See
what it would do first:

```bash
python3 <checkout>/context-db/context-db-project/context-db-migrate-from-v0.0/migrate-v0.0.py context-db --dry-run
```

`<checkout>` is a clone of the context-db repository.

The rest needs judgment, so there is a guide written for an agent to follow.
Give your agent this instruction:

```text
Read <checkout>/context-db/context-db-project/context-db-migrate-from-v0.0/context-db-migrate-from-v0.0.md
and migrate this project.
```

You can also
[read the guide on GitHub](https://github.com/cart0113/context-db/blob/v0.1/context-db/context-db-project/context-db-migrate-from-v0.0/context-db-migrate-from-v0.0.md).

The old version is still there, on the `v0.0` branch.
