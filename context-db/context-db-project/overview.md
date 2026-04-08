---
description:
  What context-db is — a portable standard for organizing project knowledge as
  hierarchical Markdown so LLM agents can discover and fetch only what they need
---

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
├── .claude/
│   ├── hooks/
│   │   └── session-start-context-db.sh    ← hook: ensures skill loads every session
│   ├── rules/context-db.md                ← rule: load the skill every conversation
│   ├── settings.local.json                ← wires up the SessionStart hook
│   └── skills/
│       ├── context-db-manual/             ← skill: instructions + TOC script
│       │   ├── SKILL.md
│       │   └── scripts/context-db-generate-toc.sh
│       ├── context-db-reindex/            ← skill: reindex descriptions
│       │   └── SKILL.md
│       └── context-db-audit/              ← skill: audit knowledge base health
│           └── SKILL.md
└── context-db/
    ├── <project-name>-project/            ← project-specific knowledge
    │   ├── <project-name>-project.md      ← folder description (frontmatter only)
    │   ├── architecture.md                ← document (frontmatter + body)
    │   └── data-model/
    │       ├── data-model.md
    │       └── entities.md
    ├── coding-standards/                  ← project-agnostic (often symlinked)
    └── writing-standards/                 ← project-agnostic (often symlinked)
```

The `<project-name>-project/` folder holds all knowledge specific to this
project — architecture, data models, domain context, design decisions. Folders
parallel to it (like `coding-standards/`, `writing-standards/`) are
project-agnostic and are often symlinked from a personal or team standards repo.

## Wiring

Two pieces: a **skill** and a **rule** (plus an optional SessionStart hook).

The **skill** (`.claude/skills/context-db-manual/`) contains full instructions
for reading, writing, and maintaining context-db. It bundles the TOC script.

The **rule** (`.claude/rules/context-db.md`) tells the agent to load the skill
at the start of every conversation.

The **hook** (`session-start-context-db.sh`) injects a mandatory instruction
before the first turn, ensuring the skill loads reliably.

## Maintenance Skills

**`/context-db-reindex`** — Re-reads every file, rewrites all `description`
fields to match current content, creates missing folder descriptors.

**`/context-db-audit`** — Cross-references the knowledge base against project
code, docs, and git history. Five phases: structural health, content freshness,
coverage gaps, documentation drift, and description quality.

## Private or Public

Folders can be private (added to `.gitignore`). The TOC script runs dynamically,
so private folders appear locally but never get committed.

Full docs: https://cart0113.github.io/context-db/
