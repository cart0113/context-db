# Getting Started

## 1. Copy the skill and rule

Copy (or symlink) the skill, rule, and hook into your project's `.claude/`
directory:

```bash
# Copy
cp -r templates/skills/context-db-manual your-project/.claude/skills/context-db-manual
cp templates/rules/context-db.md your-project/.claude/rules/context-db.md
cp templates/hooks/session-start-context-db.sh your-project/.claude/hooks/session-start-context-db.sh

# Or symlink
ln -s /path/to/context-db-repo/templates/skills/context-db-manual your-project/.claude/skills/context-db-manual
ln -s /path/to/context-db-repo/templates/rules/context-db.md your-project/.claude/rules/context-db.md
ln -s /path/to/context-db-repo/templates/hooks/session-start-context-db.sh your-project/.claude/hooks/session-start-context-db.sh
```

Optionally copy the maintenance skills too:

```bash
cp -r templates/skills/context-db-reindex your-project/.claude/skills/context-db-reindex
cp -r templates/skills/context-db-audit your-project/.claude/skills/context-db-audit
```

Wire up the SessionStart hook in `.claude/settings.local.json`:

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

The **rule** fires automatically every conversation and tells the agent to load
the skill. The **hook** reinforces this — rules alone aren't always reliable, so
the hook injects a mandatory instruction before the first turn. The **skill**
(`SKILL.md`) contains all instructions for reading, writing, and maintaining
`context-db`. It bundles the TOC script.

### Alternative bootstrap methods

The skill+rule split is the recommended approach, but anything that gets the
instructions and script to the agent works:

- **`AGENTS.md` or `CLAUDE.md`** — paste the SKILL.md content (or a summary)
  directly. Works with any agent framework.
- **Rule with inline instructions** — put the SKILL.md content into a rule file
  instead of referencing the skill. Simpler, but loads the full text every
  conversation.
- **Just the script** — place `context-db-generate-toc.sh` somewhere accessible
  (e.g. `bin/`) and tell the agent where it is via whatever instruction
  mechanism you have.

## 2. Create your project folder

The main project folder is named `<project>-project/`. Create it with a
description file (frontmatter only, no body):

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

## 3. Verify

```bash
.claude/skills/context-db-manual/scripts/context-db-generate-toc.sh context-db/
```

## Next steps

- [Cross-Project Sharing](cross-project-sharing.md) — symlink context from other
  repos.
- [Reference](../reference/specification.md) — format specification.
