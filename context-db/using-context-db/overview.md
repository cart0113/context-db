---
description:
  'READ THIS FIRST — what context-db is, how to navigate it, and how to wire it
  into a project'
---

`context-db/` is a hierarchical Markdown knowledge base. Every `.md` file has
YAML frontmatter with a `description` field — the one-line summary shown in the
TOC.

## Navigating

Run `context-db-generate-toc.sh` on any folder to see its contents:

```
context-db-generate-toc.sh context-db/
context-db-generate-toc.sh context-db/some-folder/
```

Each entry shows a description and path. Subfolder paths end with `/` — run
`context-db-generate-toc.sh` on them to go deeper. Only open files whose
descriptions are relevant to your task.

## Wiring it into a project

The recommended approach uses two pieces: a **skill** and a **rule**.

**The skill** (`.claude/skills/context-db/`) contains the full instructions for
reading, writing, and maintaining context-db. It bundles the TOC script at
`scripts/context-db-generate-toc.sh`. When loaded, the agent gets everything it
needs to work with the knowledge base.

**The rule** (`.claude/rules/context-db.md`) tells the agent that this project
uses context-db and to load the skill at the start of every conversation. Rules
are loaded automatically — no user action needed. The rule is short on purpose:
it explains _why_ context-db matters, then defers to the skill for _how_.

The core requirement is just bootstrapping the agent — it needs to understand
the system and know how to call the script. An `AGENTS.md`, a rule with inline
instructions, or any other mechanism that achieves that works. The skill+rule
split tested better because the rule fires automatically and the skill keeps
detailed instructions out of context until needed.

### Installation

1. Copy `templates/skills/context-db/` into `.claude/skills/context-db/` (or
   symlink it).
2. Copy `templates/rules/context-db.md` into `.claude/rules/context-db.md` (or
   symlink it).
3. Create `context-db/` in your project and start adding knowledge.
