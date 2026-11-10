# Migrating from v0.0

v0.1 is a rewrite with the same idea and a different shape.

| v0.0                                            | v0.1                                                 |
| ----------------------------------------------- | ---------------------------------------------------- |
| Frontmatter: `description`                      | Frontmatter: `type` and `description` (OKF)          |
| TOC printed by a script                         | Generated `index.md` files, read directly            |
| `prompt`, `update`, `maintain`, `read`          | `prompt`, `update`, `wip`, `configure`               |
| No config                                       | `context-db.json` plus optional `context-db.local.json` |
| `context-db/ON_PROMPT.md`                       | `context-db/context-db-on-markdown/ON_PROMPT.md`     |
| `<name>-project/wip.md`                         | `<name>-project/wip/`                                |
| Backticked paths and a resolver script          | Markdown links                                       |
| Three scripts                                   | One script                                           |

A migration script does the mechanical part: it adds a guessed `type` to every
file, converts backticked paths to links, and moves the ON files and `wip.md`.

```bash
python3 <context-db-checkout>/context-db/context-db-project/context-db-migrate-from-v0.0/migrate-v0.0.py context-db --dry-run
```

The full procedure is written for an agent to follow. Point the agent at it:

> Read
> `<context-db-checkout>/context-db/context-db-project/context-db-migrate-from-v0.0/context-db-migrate-from-v0.0.md`
> and migrate this project.

It is also
[on GitHub](https://github.com/cart0113/context-db/blob/v0.1/context-db/context-db-project/context-db-migrate-from-v0.0/context-db-migrate-from-v0.0.md).

The v0.0 system remains on the `v0.0` branch.
