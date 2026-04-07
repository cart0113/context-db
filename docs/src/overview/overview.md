# Overview

context-db is a portable standard for organizing project knowledge as Markdown
files with on-demand tables of contents for LLM agents.

- **On-demand TOCs from filesystem** -- `bin/show_toc.sh` generates tables of
  contents on the fly from YAML frontmatter. No static files to commit or keep
  in sync.
- **Progressive disclosure** -- agents browse TOCs top-down, reading
  descriptions to decide what to fetch. Scales from a handful of files to
  hundreds without flooding context.
- **Two-way knowledge** -- agents read context and write it back, like
  persistent memory. The knowledge base stays current as the codebase evolves.
- **Cross-project sharing** -- symlink folders from other repos into
  `context-db/` and they appear in the TOC automatically.
- **Zero dependencies** -- bash 3.2+ and awk, pre-installed on macOS and Linux.
- **Tool-agnostic** -- works with Claude Code, Codex, Cursor, or any tool that
  can run shell commands and read stdout.
- **Copy-based install** -- copy `templates/bin/` and `templates/context-db/`
  into your project. A sample `AGENTS.md` and `SKILLS.md` are also provided.

```
your-project/
├── AGENTS.md                        ← "read context-db-instructions.md"
├── bin/show_toc.sh                  ← TOC generator
└── context-db/
    ├── context-db-instructions.md   ← reading/writing rules
    ├── my-project-project/          ← main project context
    │   ├── my-project-project.md    ← folder description (frontmatter only)
    │   ├── architecture.md          ← document (frontmatter + body)
    │   └── data-model/
    │       ├── data-model.md
    │       └── entities.md
    └── coding-standards/            ← ancillary (symlinked from another repo)
        └── coding-standards.md
```

## How It Works

1. `AGENTS.md` points the agent to `context-db/context-db-instructions.md`
2. The instructions file teaches navigation and maintenance rules
3. The agent runs `bin/show_toc.sh context-db/` to browse the knowledge tree
4. Descriptions in YAML frontmatter let the agent skip irrelevant branches
5. When the agent learns something important, it writes it back to context-db
