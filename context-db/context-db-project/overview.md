---
description:
  What context-db is, why it exists, folder structure, how agents use it,
  the context problem (why less is more), and maintenance
---

# context-db

A minimal standard for organizing project knowledge as hierarchical Markdown so
LLM agents can discover and fetch only what they need.

Large `CLAUDE.md` and `AGENTS.md` files loaded every session hurt agent
performance — but agents still need project-specific knowledge for best results.
context-db gives every file and folder a YAML `description` field. Files are
organized in folders and subfolders, and a Python script dynamically generates a
table of contents for any folder — creating a filesystem-based discovery tree
with logarithmic progressive disclosure. Agents navigate to what they need and
skip the rest.

## Why context-db

- **Hierarchical.** Filesystem as a B-tree. Agents read frontmatter descriptions
  at each level and branch into what's relevant, skipping everything else.
- **Logarithmic cost.** 5-10 items per folder, ~100 lines per file. The amount
  read scales with the task, not the total knowledge base.
- **Minimal.** Contains what agents can't derive from code — conventions,
  pitfalls, rationale, domain knowledge. Installed instructions enforce these
  standards when agents generate content, and `/context-db maintain` actively
  prunes content using this guidance.

## Folder Structure

```
your-project/
├── .claude/
│   ├── hooks/
│   │   └── session-start-context-db.sh    ← ensures skill loads every session
│   ├── rules/context-db.md                ← load the skill every conversation
│   ├── settings.local.json                ← wires up the SessionStart hook
│   └── skills/
│       └── context-db/                    ← unified skill: all commands + scripts
│           ├── SKILL.md
│           └── scripts/
│               ├── context-db-generate-toc.py
│               ├── context-db-main-agent.py
│               └── context-db-sub-agent.py
└── context-db/
    ├── <project-name>-project/            ← project-specific knowledge
    │   ├── <project-name>-project.md      ← folder description (frontmatter only)
    │   ├── architecture.md                ← document (frontmatter + body)
    │   └── data-model/
    ├── coding-standards/                  ← project-agnostic (often symlinked)
    └── writing-standards/                 ← project-agnostic (often symlinked)
```

The `<project-name>-project/` folder holds project-specific knowledge. Folders
parallel to it (like `coding-standards/`) are project-agnostic and often
symlinked from a shared standards repo.

## Wiring It In

The agent needs instructions on how to run the TOC script and navigate. This is
packaged as a **skill** (`.claude/skills/context-db/`). A **rule** and a
**SessionStart hook** ensure the skill loads every conversation.

Any mechanism that gets the SKILL.md content in front of the agent works:
`AGENTS.md`/`CLAUDE.md`, a rule with inline instructions, or just placing the
TOC script somewhere accessible and telling the agent about it.

## Private or Public

The TOC script runs dynamically — anything it finds at runtime appears in the
agent's navigation, whether committed, gitignored, or symlinked. Gitignored
symlinks can point anywhere. See
[cross-project-sharing.md](cross-project-sharing.md) for patterns.

## The Context Problem

> ["To alcohol! The cause of, and solution to, all of life's problems."](https://www.youtube.com/watch?v=SXyrYMxa-VI)
> — Homer Simpson

Context files are both the cause of, and solution to, many agent problems.
There is [increasing discussion](https://arxiv.org/abs/2602.11988) about whether
`CLAUDE.md`, `AGENTS.md`, `.cursorrules` actually help. Agents given context
files that describe code state trust those descriptions, read less actual code,
and perform _worse_ when descriptions drift. Cost goes up, success rate goes
down.

Yet agents left with no guidance default to their training: generic patterns, no
awareness of project-specific constraints. The result is code that compiles but
doesn't match how the project works.

The principle: context-db contains the gap between what the code shows and what
the agent needs to know. Conventions it wouldn't infer. Pitfalls it will hit.
Rationale not visible in source. Everything else — code summaries, module
inventories — is noise that displaces code the agent could read instead.

The hierarchical structure helps too. A flat 5,000-line `CLAUDE.md` forces every
agent to read database rules when working on CSS. The B-tree means the context
cost is proportional to the task, not the total knowledge base.

## Maintenance

`/context-db maintain` runs a 7-phase audit: structural health, content
freshness, content value, coverage gaps, doc drift, cross-references, and
reindex. Default posture is to cut — leave context-db smaller and sharper.

## Documentation

Full docs: https://cart0113.github.io/context-db/

## License

MIT
