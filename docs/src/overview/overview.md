# Overview

`context-db` is a portable standard for organizing project knowledge as
hierarchical Markdown files. Documents and folders contain YAML frontmatter with
brief content summaries. A `context-db-generate-toc.sh` script reads the
frontmatter and generates a table of contents for any folder. Agents browse the
TOC, read only relevant files, and can write knowledge back over time.

The goal was a lighter-weight system than using skills for all project
knowledge:

- **Hierarchical.** Nested folders support progressive disclosure — agents read
  one TOC at a time and go deeper only when needed.
- **Lightweight.** Plain Markdown with frontmatter. No special tooling, no
  service scripts, no vendor lock-in.
- **Scales.** Each TOC stays small (5–10 items by convention), so the knowledge
  base can grow to hundreds of documents while any navigation step stays cheap.
  The amount an agent reads is logarithmic relative to the total size.

Skills are instructions on how to do something and define discrete tools.
`context-db` is for free-form project knowledge and context — architecture,
conventions, domain context, design decisions. One
[Reddit user](https://www.reddit.com/r/ClaudeCode/comments/1p8wipb/how_many_claude_skills_are_too_many/)
mapped out 250 skills and had to consolidate down to 22 to get reliable
selection. `context-db` sidesteps this by keeping each navigation step to 5–10
items.

`context-db` is also similar to using [Obsidian](https://obsidian.md/) vaults,
but more minimal and designed for agent consumption rather than human browsing.

## Folder structure

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

## How It Works

1. Copy the skill and rule from `templates/` into your project (or symlink
   them).
2. The rule fires automatically and tells the agent to load the skill.
3. The skill teaches the agent how to run `context-db-generate-toc.sh` and
   navigate the knowledge base.
4. Descriptions in YAML frontmatter let the agent skip irrelevant branches.
5. When the agent learns something important, it writes it back to `context-db`.

## Private or Public

Folders can be private (added to `.gitignore`). The TOC script runs dynamically,
so private folders appear in the TOC for local sessions but never get committed.
