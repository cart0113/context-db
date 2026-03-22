# context-md

A portable standard for hierarchically organizing context as Markdown files, with auto-generated tables of contents for progressive disclosure.

An LLM reads a lightweight `_toc.md` index, sees one-line descriptions of every subfolder and file, and fetches only what's relevant to the current task. Agents don't read the description files — they read the TOC, then fetch individual documents.

## Why

Large projects need more background knowledge than a single context file can hold. `CLAUDE.md` is recommended under 200 lines. `AGENTS.md` caps at 32 KiB. But a legacy enterprise system might need thousands of lines of context — architecture, data models, API contracts, deployment constraints, historical decisions — for an agent to reason safely about changes.

The fix is smaller documents organized in folders. But then agents need a way to discover what exists without loading everything. context-md solves this with auto-generated `_toc.md` indexes: lightweight maps (~100 tokens) that show the agent what knowledge is available, so it can fetch only what's relevant.

A TOC is a **discovery** mechanism ("here's what exists"), complementing retrieval mechanisms like grep and RAG ("find me X"). Research shows LLM performance degrades as context grows — progressive disclosure keeps the window focused on what matters.

See [docs/motivation.md](docs/motivation.md) for the full rationale.

## Example

A payments service with shared coding and git standards (see `example/`):

```
acme_payments/
└── CONTEXT/
    ├── CONTEXT.md
    ├── CONTEXT_toc.md                    ← generated
    ├── _drafts/                          ← skipped (underscore prefix)
    │   └── migration_plan.md
    ├── acme_payments/
    │   ├── acme_payments.md
    │   ├── acme_payments_toc.md          ← generated
    │   ├── architecture.md
    │   ├── api_reference.md
    │   └── data_model/
    │       ├── data_model.md
    │       ├── data_model_toc.md         ← generated
    │       ├── entities.md
    │       └── schema_conventions.md
    ├── coding_standards/ → shared/...    ← symlink
    │   ├── coding_standards.md
    │   ├── naming_conventions.md
    │   └── error_handling.md
    └── git_standards/ → shared/...       ← symlink
        ├── git_standards.md
        ├── commit_messages.md
        └── branching.md
```

The generated root TOC (`CONTEXT_toc.md`):

```
## Subfolders

- description: Acme Payments — architecture, APIs, and data model
  path: acme_payments/acme_payments_toc.md
- description: Shared coding standards — naming, error handling, and testing conventions
  path: coding_standards/coding_standards_toc.md
- description: Git workflow — branching strategy, commit messages, and PR conventions
  path: git_standards/git_standards_toc.md
```

Following `acme_payments/acme_payments_toc.md` shows the next level:

```
## Subfolders

- description: Database schema, entities, and relationships
  path: data_model/data_model_toc.md

## Files

- description: REST API endpoints, authentication, and error codes
  path: api_reference.md
- description: System components, data flow, and service boundaries
  path: architecture.md
```

The LLM reads each TOC, decides which paths are relevant, and follows `_toc.md` paths deeper. `_drafts/` doesn't appear.

## Rules

1. **Description file.** A folder is a context node if it contains any of: `<folder_name>.md`, `CONTEXT.md`, `SKILL.md`, `AGENT.md`, or `AGENTS.md`. The file should only have YAML front matter with a single `description` key. Other content in this file is ignored and should not be included.

2. **Context documents.** Individual `.md` files use the same format — YAML front matter with `description`. The description appears in the parent's `_toc.md`.

3. **TOC generation.** `bin/build_toc.sh` walks the directory tree and generates `<folder>_toc.md` for each context node. By default it only rebuilds when source files are newer than the existing TOC. Use `--build-all` to force a full rebuild.

4. **Symlinks.** Symlinked folders appear in the parent's TOC. The script never writes into a folder whose real path is outside the project root.

5. **Skipping.** Underscore-prefixed (`_drafts/`) and dot-prefixed (`.hidden/`) names are always skipped.

## File Format

Description file (`acme_payments.md`) — identifies the folder as a context node:

```markdown
---
description: Acme Payments — architecture, APIs, and data model
---
```

Context document (`architecture.md`) — description plus content:

```markdown
---
description: System components, data flow, and service boundaries
---

# Architecture

Acme Payments is a three-tier service:

1. **API Gateway** — validates requests, rate limiting, auth
2. **Payment Engine** — orchestrates payment flows, retries, idempotency
3. **Ledger** — append-only transaction log, double-entry bookkeeping

All inter-service communication is async via message queue.
```

## Building

```bash
bin/build_toc.sh                    # Rebuild changed _toc.md files
bin/build_toc.sh --build-all        # Rebuild all _toc.md files unconditionally
bin/build_toc.sh CONTEXT/           # Build from a specific directory
```

### Pre-commit hook

```bash
cp hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

## Bootstrap

The agent needs instructions on how to read and write context-md. Copy the text from [`bootstrap/CONTEXT.md`](bootstrap/CONTEXT.md) into whatever file your agent reads on startup — `CONTEXT.md`, `AGENTS.md`, `.cursorrules`, a `.claude/rules/` file, or a system prompt. The text is what matters, not the delivery mechanism.

### Workspace patterns

context-md doesn't prescribe where context lives or how it's wired in. A few patterns:

**Symlink shared context into your project:**
```bash
ln -s /shared/coding_standards CONTEXT/coding_standards
```

**Point rules at multiple locations:**
```markdown
# In CLAUDE.md, .cursorrules, or AGENTS.md:
Read CONTEXT/CONTEXT_toc.md for project context.
Read ~/team/CONTEXT/CONTEXT_toc.md for team coding standards.
```

**Reference a specific subfolder** when you don't need the whole tree:
```markdown
Read CONTEXT/acme_payments/acme_payments_toc.md to start.
```

## Tools

| Script | Description |
|--------|-------------|
| `bin/build_toc.sh` | Recursive TOC builder with change detection |
| `hooks/pre-commit` | Git hook that runs `build_toc.sh` before commit |

## Future

A `<folder_name>.cfg` system for per-folder configuration (ignore lists, symlink follow rules) is under consideration.

## License

MIT
