# context-db

A portable standard for organizing project knowledge as Markdown files, with
on-demand tables of contents for progressive disclosure.

An LLM agent runs `bin/show_toc.sh` on a folder, sees one-line descriptions of
every subfolder and file, and fetches only the documents relevant to its current
task. Nested folders produce nested TOCs, scaling from a handful of files to
hundreds without flooding the agent's context window.

```
your-project/
├── AGENTS.md                        ← bootstrap: points agent here
├── bin/show_toc.sh                  ← TOC generator (prints to stdout)
└── context-db/
    ├── context-db-instructions.md   ← reading/writing rules
    ├── my-project/
    │   ├── my-project.md            ← folder description (frontmatter)
    │   ├── architecture.md          ← context document
    │   └── data-model/
    │       ├── data-model.md
    │       └── entities.md
    └── coding-standards/            ← symlinked from another repo
        └── coding-standards.md
```

## The problem

AI coding tools give agents background knowledge through a single entry-point
file — `CLAUDE.md`, `AGENTS.md`, `.cursorrules`. For a small project, that
works. For a large one, the background knowledge needed — architecture, data
models, API contracts, deployment constraints, research notes — doesn't fit in a
few hundred lines.

Loading everything eagerly isn't the answer either. Models do best when relevant
information appears early in context; performance degrades as input length
grows. And built-in tools like grep answer "find something matching this query"
— but the agent has to already know what to search for.

## How context-db solves it

A TOC answers "here's what exists," giving the agent a map of available
knowledge in a few hundred tokens before it decides what to pull in.

1. Every folder has a **description file** (`<folder>.md`) with YAML frontmatter
   containing a one-line `description`.
2. Every document has a `description` in its frontmatter — this is what appears
   in the TOC.
3. The agent runs `bin/show_toc.sh <folder>` to get a TOC listing descriptions
   and paths, printed to stdout.
4. The agent reads TOCs top-down, deciding at each level what to fetch and what
   to skip based on descriptions alone.

The agent is also expected to **write back** — when it discovers something
important (architecture decisions, gotchas, non-obvious patterns), it adds or
updates documents in context-db so future agents don't have to rediscover the
same knowledge.

## Cross-project sharing

Context-db folders are self-describing and portable. You can share knowledge
across projects by symlinking folders from other repos into your `context-db/`
directory. Since `show_toc.sh` generates the TOC on the fly, symlinked folders
appear automatically — nothing to commit or rebuild.

Two patterns:

- **Private symlink + .gitignore** — Symlink another repo's context into yours
  and `.gitignore` the symlink. Your agent sees it; teammates don't. Nothing
  changes in git.
- **Committed reference** — Use git submodule or git-sync to bring in external
  repos, then symlink their context-db folders. The whole team gets it.

See the [Cross-Project Sharing](guide/cross-project-sharing.md) guide for
details.

## Key properties

- **Zero dependencies** — bash 3.2+ and awk, pre-installed on macOS and Linux.
- **No generated files** — TOCs are produced on demand by `show_toc.sh`, nothing
  to commit or keep in sync.
- **Portable** — self-describing folders can be symlinked and composed across
  projects without coordination.
- **Tool-agnostic** — works with Claude Code, Codex, Cursor, or any tool that
  can run shell commands and read stdout.
- **Progressive disclosure** — agents load what they need, not everything at
  once.
- **Two-way** — agents read context and write it back, keeping the knowledge
  base current as the codebase evolves.

## Documentation

- [Getting Started](guide/getting-started.md) — set up context-db in your
  project
- [Cross-Project Sharing](guide/cross-project-sharing.md) — symlinks, git
  submodule, git-sync
- [Reference](reference/specification.md) — format specification, TOC format,
  and script usage
