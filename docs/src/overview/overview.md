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
project-agnostic and are often symlinked from a personal or team standards repo
so the same knowledge can be shared across every project that uses context-db.

Every folder has a `<folder-name>.md` file containing only YAML frontmatter —
this is the folder's description shown in the TOC.

## SessionStart Hook

The rule tells the agent to load the skill, but rules alone aren't always
reliable — the agent can skip or deprioritize them. The `SessionStart` hook
(`templates/hooks/session-start-context-db.sh`) solves this by injecting a
mandatory instruction into the conversation context before the first turn,
ensuring `/context-db-manual` is loaded every time Claude Code starts up.

Wire it up in `.claude/settings.local.json`:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|resume",
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/session-start-context-db.sh"
          }
        ]
      }
    ]
  }
}
```

## Wiring It In

Two pieces: a **skill** and a **rule** (plus the optional hook above).

The **skill** (`.claude/skills/context-db-manual/`) contains the full
instructions for reading, writing, and maintaining context-db. It bundles the
TOC script. When loaded, the agent gets everything it needs.

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

1. Copy `templates/skills/context-db-manual/` into
   `.claude/skills/context-db-manual/` (or symlink it).
2. Copy `templates/rules/context-db.md` into `.claude/rules/context-db.md` (or
   symlink it).
3. Copy `templates/hooks/session-start-context-db.sh` into `.claude/hooks/` and
   wire it up in `.claude/settings.local.json` (see SessionStart Hook above).
4. Create `context-db/` in your project and start adding knowledge.

## Private or Public

Folders can be private (added to `.gitignore`). The `context-db-generate-toc.sh`
script runs dynamically, so private folders appear in the TOC for local sessions
but never get committed.

## Repo Structure

```
templates/                           Copy these into your project
  rules/context-db.md                Rule template
  hooks/session-start-context-db.sh  SessionStart hook template
  skills/context-db-manual/          Skill template (instructions + TOC script)
  skills/context-db-reindex/         Reindex skill template
  skills/context-db-audit/           Audit skill template
context-db/                          This project's own knowledge database
example/                             Example project structure
docs/                                GitHub Pages documentation
```

## Maintenance Skills

Two optional skills help keep the knowledge base healthy over time:

**`/context-db-reindex`** — Re-reads every file, rewrites all `description`
fields in frontmatter to match current content, and creates any missing
`<folder-name>.md` descriptor files. Works bottom-up so parent folder
descriptions reflect their children. Mostly automated — asks only when a file's
purpose is genuinely ambiguous. Accepts an optional folder path to scope the
reindex.

**`/context-db-audit`** — Cross-references the knowledge base against project
code, docs, and git history. Checks structural health, content freshness,
coverage gaps, documentation drift, description quality, and cross-references
between documents. Interactive by default — explains findings and asks before
acting on anything ambiguous, but fixes clearly wrong things directly. Accepts
an optional folder path.

Both skills live in `templates/skills/` and can be wired into any project the
same way as the core `context-db-manual` skill.

## Documentation

Full docs: https://cart0113.github.io/context-db/

## License

MIT
