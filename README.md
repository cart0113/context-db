# context-db

A portable standard for organizing project knowledge as hierarchical Markdown so
LLM agents can discover and fetch only what they need.

Every `.md` file has YAML frontmatter with a `description` field. A
`context-db-generate-toc.sh` script reads the frontmatter and generates a table
of contents for any folder. Agents browse the TOC, read only relevant files, and
can write knowledge back over time.

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
├── .claude/                               ← Claude Code; .cursor/ for Cursor, .agents/ for Codex
│   ├── rules/context-db.md               ← rule: load the skill every conversation
│   └── skills/context-db/                ← skill: instructions + TOC script
│       ├── SKILL.md
│       └── scripts/context-db-generate-toc.sh
└── context-db/
    ├── <project-name>-project/            ← main project context
    │   ├── <project-name>-project.md      ← folder description (frontmatter only)
    │   ├── architecture.md                ← document (frontmatter + body)
    │   └── data-model/
    │       ├── data-model.md
    │       └── entities.md
    ├── coding-standards/                  ← ancillary (can be symlinked)
    └── writing-standards/                 ← ancillary (can be symlinked)
```

Every folder has a `<folder-name>.md` file containing only YAML frontmatter —
this is the folder's description shown in the TOC.

## Wiring It In

Two pieces: a **skill** and a **rule**.

The **skill** (`.claude/skills/context-db/`) contains the full instructions for
reading, writing, and maintaining context-db. It bundles the TOC script. When
loaded, the agent gets everything it needs.

The **rule** (`.claude/rules/context-db.md`) tells the agent that this project
uses context-db and to load the skill at the start of every conversation. Rules
load automatically — no user action needed.

The skill+rule split tested better because the rule fires automatically and the
skill keeps detailed instructions out of context until needed. But anything that
bootstraps the agent works. Alternative approaches:

- **`AGENTS.md` or `CLAUDE.md`** — paste the SKILL.md content (or a summary)
  directly. Works with any agent framework.
- **Rule with inline instructions** — put the SKILL.md content into a rule file
  instead of referencing the skill. Simpler, but loads the full text every
  conversation.
- **Just the script** — place `context-db-generate-toc.sh` somewhere accessible
  (e.g. `bin/`) and tell the agent where it is and how to use it via whatever
  instruction mechanism you have.

## Getting Started

1. Copy `templates/skills/context-db/` into `.claude/skills/context-db/` (or
   symlink it).
2. Copy `templates/rules/context-db.md` into `.claude/rules/context-db.md` (or
   symlink it).
3. Create `context-db/` in your project and start adding knowledge.

## Private or Public

Folders can be private (added to `.gitignore`). The `context-db-generate-toc.sh`
script runs dynamically, so private folders appear in the TOC for local sessions
but never get committed.

## Repo Structure

```
templates/                     Copy these into your project
  rules/context-db.md          Rule template
  skills/context-db/           Skill template (instructions + TOC script)
context-db/                    This project's own knowledge database
example/                       Example project structure
docs/                          GitHub Pages documentation
```

## Documentation

Full docs: https://cart0113.github.io/context-db/

## License

MIT
