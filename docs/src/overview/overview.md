# context-db

A portable standard for organizing project knowledge as Markdown files, with
auto-generated tables of contents for progressive disclosure.

An LLM agent reads a lightweight TOC listing descriptions and paths, then
fetches only the documents relevant to its current task. Nested folders produce
nested TOCs, scaling from a handful of files to hundreds.

```
your-project/
├── AGENTS.md                        ← bootstrap: points agent here
└── context-db/
    ├── context-db-instructions.md   ← reading/writing rules
    ├── context-db-toc.md            ← generated index
    ├── my-project/
    │   ├── my-project.md            ← folder description
    │   ├── my-project-toc.md        ← generated index
    │   ├── architecture.md          ← context document
    │   └── data-model/
    │       ├── data-model.md
    │       ├── data-model-toc.md
    │       └── entities.md
    └── shared/                      ← symlinked from another repo
        └── coding-standards/
            ├── coding-standards.md
            └── coding-standards-toc.md
```

## How it works

1. Every folder has a description file (`<folder>.md`) with YAML frontmatter
   containing a one-line `description`.
2. Every document has a `description` in its frontmatter — this is what appears
   in the parent TOC.
3. `build_toc.sh` walks the tree and generates `-toc.md` files listing
   descriptions and paths.
4. The agent reads TOCs top-down, deciding at each level what to fetch.

## Key properties

- **Zero dependencies** — bash 3.2+ and awk, pre-installed on macOS and Linux.
- **Portable** — self-describing folders can be symlinked and composed across
  projects.
- **Tool-agnostic** — works with Claude Code, Codex, Cursor, or any tool that
  reads Markdown.
- **Progressive disclosure** — agents load what they need, not everything at
  once.

## Documentation

- [Getting Started](guide/getting-started.md) — step-by-step setup
- [Specification](reference/specification.md) — format reference
- [TOC Format](reference/toc-format.md) — generated file structure
- [Script Reference](reference/script-reference.md) — build_toc.sh usage
- [Motivation](motivation/motivation.md) — why this exists
