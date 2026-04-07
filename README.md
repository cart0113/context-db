# context-db

A portable standard for organizing project knowledge as hierarchical Markdown so
LLM agents can discover and fetch only what they need.

Every `.md` file has YAML frontmatter with a `description` field. A
`show_toc.sh` script reads the frontmatter and generates a table of contents for
any folder. Agents browse the TOC, read only relevant files, and can write
knowledge back over time.

## Why context-db

- **Hierarchical.** Nested folders support progressive disclosure — agents read
  one TOC at a time and go deeper only when needed.
- **Lightweight.** Plain Markdown with frontmatter. No special tooling, no
  service scripts, no vendor lock-in.
- **Scales.** Each TOC stays small (5–10 items by convention), so the knowledge
  base can grow to hundreds of documents while any navigation step stays cheap.
  The amount an agent reads is logarithmic relative to the total size.

## Folder Structure

```
your-project/
├── AGENTS.md                          ← tells agent to use context-db first
├── bin/show_toc.sh                    ← dynamic TOC generator
└── context-db/
    ├── using-context-db/              ← how to read/write context-db
    ├── <project-name>-project/        ← main project context
    │   ├── <project-name>-project.md  ← folder description (frontmatter only)
    │   ├── architecture.md            ← document (frontmatter + body)
    │   └── data-model/
    │       ├── data-model.md
    │       └── entities.md
    ├── coding-standards/              ← ancillary (can be symlinked)
    └── writing-standards/             ← ancillary (can be symlinked)
```

Every folder has a `<folder-name>.md` file containing only YAML frontmatter —
this is the folder's description shown in the TOC.

## Integration Paths

There are three ways to wire context-db into a project. Each one tells the agent
where `show_toc.sh` lives and to run it before starting work.

**AGENTS.md** — Put an `AGENTS.md` in the project root. The script lives at
`bin/show_toc.sh`. Simplest option, works with any agent that reads `AGENTS.md`.
See `templates/AGENTS.md`.

**Rule** — Add a `.claude/rules/context-db.md` file. Loaded automatically by
Claude Code without needing AGENTS.md. The script lives at `bin/show_toc.sh`.
See `templates/rules/context-db.md`.

**Skill** — Add a `context-db` skill under `.claude/skills/`. The script lives
at `${CLAUDE_SKILL_DIR}/scripts/show_toc.sh` (bundled with the skill). Most
self-contained option — no `bin/` directory needed. See
`templates/skills/context-db/`.

Pick whichever fits your project. You can combine them (e.g., AGENTS.md for
general agents + skill for Claude Code).

## Getting Started

1. Copy one of the integration templates above into your project.
2. Copy `templates/bin/show_toc.sh` to `bin/show_toc.sh` (unless using the skill
   path, which bundles its own copy).
3. Copy `templates/context-db/using-context-db/` to
   `context-db/using-context-db/` — this teaches agents how context-db works.
4. Create your first knowledge folder (e.g. `context-db/<project>-project/`).
5. Build up your knowledge base over time.

## Private or Public

Folders can be private (added to `.gitignore`). The `show_toc.sh` script runs
dynamically, so private folders appear in the TOC for local sessions but never
get committed.

## Repo Structure

```
templates/              Copy these into your project
  AGENTS.md             AGENTS.md integration template
  rules/context-db.md   Rule integration template
  skills/context-db/    Skill integration template
  bin/show_toc.sh       TOC generator script
  context-db/           using-context-db docs to copy
bin/show_toc.sh         Canonical TOC generator
context-db/             This project's own knowledge database
example/                Example project structure
docs/                   GitHub Pages documentation
```

## Documentation

Full docs: https://cart0113.github.io/context-db/

## License

MIT
