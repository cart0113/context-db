# context-db

A portable standard for organizing project knowledge as Markdown files, with
on-demand tables of contents for progressive disclosure.

An LLM agent runs `bin/show_toc.sh` on a folder to see descriptions and paths,
then fetches only the documents relevant to its current task. Nested folders
produce nested TOCs, scaling from a handful of files to hundreds.

```
your-project/
├── AGENTS.md                        ← bootstrap: points agent here
├── bin/show_toc.sh                  ← TOC generator (prints to stdout)
└── context-db/
    ├── context-db-instructions.md   ← reading/writing rules
    ├── my-project/
    │   ├── my-project.md            ← folder description
    │   ├── architecture.md          ← context document
    │   └── data-model/
    │       ├── data-model.md
    │       └── entities.md
    └── shared/                      ← symlinked from another repo
        └── coding-standards/
            └── coding-standards.md
```

## How it works

1. Every folder has a description file (`<folder>.md`) with YAML frontmatter
   containing a one-line `description`.
2. Every document has a `description` in its frontmatter — this is what appears
   in the TOC.
3. The agent runs `bin/show_toc.sh <folder>` to get a TOC listing descriptions
   and paths, printed to stdout.
4. The agent reads TOCs top-down, deciding at each level what to fetch.

## Why

AI coding tools give agents background knowledge through a single entry-point
file — `CLAUDE.md`, `AGENTS.md`, `.cursorrules`. For a small project, that
works. For a large one, the background knowledge needed — architecture, data
models, API contracts, deployment constraints — doesn't fit in a few hundred
lines.

Loading everything eagerly isn't the answer either. Models do best when relevant
information appears early in context; performance degrades as input length
grows. And built-in tools like grep answer "find something matching this query"
— but the agent has to already know what to search for. A TOC answers "here's
what exists," giving the agent a map of available knowledge in a few hundred
tokens before it decides what to pull in.

## Key properties

- **Zero dependencies** — bash 3.2+ and awk, pre-installed on macOS and Linux.
- **No generated files** — TOCs are produced on demand by `show_toc.sh`, nothing
  to commit or keep in sync.
- **Portable** — self-describing folders can be symlinked and composed across
  projects.
- **Tool-agnostic** — works with Claude Code, Codex, Cursor, or any tool that
  can run shell commands.
- **Progressive disclosure** — agents load what they need, not everything at
  once.

## Documentation

- [Getting Started](guide/getting-started.md) — step-by-step setup
- [Reference](reference/specification.md) — format specification, TOC format,
  and script usage
