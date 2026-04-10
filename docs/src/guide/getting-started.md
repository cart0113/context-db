# Getting Started

## 1. Create your context-db

Create a `context-db/` directory with a `<project-name>-project/` subfolder. Add
a description file (frontmatter only, no body):

```
context-db/
└── acme-payments-project/
    └── acme-payments-project.md
```

```yaml
---
description: Acme Payments — architecture, APIs, and data model
---
```

Add context documents alongside it. Each has `description` frontmatter and
Markdown content. Keep folders to 5–10 items — split into subfolders when one
grows beyond that.

## 2. Bootstrap — tell the agent about context-db

The context-db is just markdown files and a bash TOC script. Any agent that can
read files and run shell commands can use it. The bootstrap is how you get the
agent to read `context-db/` at the start of a conversation.

### Claude Code (recommended: SessionStart hook)

Copy the hook and skill into your project:

```bash
cp -r templates/skills/context-db-manual your-project/.claude/skills/context-db-manual
cp templates/hooks/session-start-context-db.sh your-project/.claude/hooks/session-start-context-db.sh
```

Wire up the hook in `.claude/settings.local.json`:

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

The hook fires before the first turn and tells the agent to read the SKILL.md
and run the TOC script. In practice this is the most reliable bootstrap — the
agent sees it before anything else.

**Alternative: rule file.** Copy `templates/rules/context-db.md` into
`.claude/rules/`. Rules fire every conversation and give the same instruction.
You can use a rule instead of the hook, or both if you want to be very sure. The
hook alone is usually sufficient.

Optionally copy the maintenance skills:

```bash
cp -r templates/skills/context-db-reindex your-project/.claude/skills/context-db-reindex
cp -r templates/skills/context-db-maintain your-project/.claude/skills/context-db-maintain
```

### Cursor

Add the instructions to `.cursorrules` or `.cursor/rules/context-db.md`:

```
This project uses context-db/ — a hierarchical Markdown knowledge base.
Run this script to see available topics:

  .claude/skills/context-db-manual/scripts/context-db-generate-toc.sh context-db/

Read topics relevant to the task, then read the code.
```

The TOC script is just bash — works in any terminal.

### GitHub Copilot

Add the same instructions to `.github/copilot-instructions.md`.

### Any agent (AGENTS.md / CLAUDE.md / GEMINI.md)

Paste the SKILL.md content (or a summary) into whatever instruction file your
agent reads. The key things the agent needs to know:

1. `context-db/` exists and contains project knowledge.
2. Run the TOC script to see topics.
3. Read only what's relevant, then read the code.

## 3. Verify

```bash
.claude/skills/context-db-manual/scripts/context-db-generate-toc.sh context-db/
```

## Next steps

- [Cross-Project Sharing](cross-project-sharing.md) — symlink context from other
  repos.
- [Reference](../reference/specification.md) — format specification.
