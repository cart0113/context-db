# Getting Started

## 1. Create your context-db

Create a `context-db/` directory with a `<project-name>-project/` subfolder. Add
a descriptor file — frontmatter only, no body:

```
context-db/
└── acme-payments-project/
    └── acme-payments-project.md
```

```yaml
---
description:
  Main project folder for this repo. Acme Payments — architecture, APIs, data
  model.
---
```

The `Main project folder for this repo.` opening is a soft convention the
dispatcher and `maintain` command rely on. The body of the descriptor file stays
empty; topic content goes in sibling files.

Add context documents alongside it. Each gets its own `description` frontmatter
and a Markdown body. Keep folders to 5–10 items — split into subfolders when one
grows beyond that.

## 2. Install the dispatcher

The dispatcher is a Python script. The canonical location is inside a Claude
Code skill folder:

```bash
cp -r templates/skills/context-db your-project/.claude/skills/context-db
```

The same scripts run unchanged from any path. Non-Claude users can put them
anywhere and call them directly. There's nothing Claude-specific about the
script itself — it's a Python file that reads context-db markdown and prints
text. No configuration file is needed; the commands take no config.

## 3. (Optional) Add `ON_PROMPT.md`

A file at `context-db/ON_PROMPT.md` is inlined automatically on every `prompt` —
the only always-on mechanism, and the one most projects actually use. Add it if
you have a rule the agent should see every time it consults the knowledge base:

```bash
cp templates/ON_PROMPT.md your-project/context-db/ON_PROMPT.md
```

Then edit it down to your rule. Keep it brief — every line is re-read on every
`prompt`. Two siblings work identically if you ever need them:
`context-db/ON_UPDATE.md` (inlined on every `update`) and
`context-db/ON_MAINTAIN.md` (inlined on every `maintain`) — most projects never
add them. See [Commands](commands.md#the-onmd-special-files).

## 4. (Optional) Make the agent aware of it

context-db is opt-in — there is no startup hook. To make the agent aware the
knowledge base exists, paste the shipped boilerplate into your agent's
standing-instructions file:

```bash
cat templates/AGENTS.md >> your-project/AGENTS.md
```

`AGENTS.md` is the cross-agent convention (Codex and many others read it);
Claude Code reads `CLAUDE.md`, Cursor reads `.cursor/rules/`, and Copilot reads
`.github/copilot-instructions.md`. Paste the same body into whichever your agent
uses. It tells the agent the database exists and — deliberately — that it must
**not** read `context-db/` on its own; the agent engages only when you invoke a
`/context-db` command.

If you skip this step, nothing fires automatically either way — you invoke the
commands by hand (or as the `/context-db` skill in Claude Code) when you want
them.

## 5. Verify

```bash
python3 .claude/skills/context-db/scripts/context-db-generate-toc.py context-db/
python3 .claude/skills/context-db/scripts/context-db-main-agent.py prompt "test"
```

The first prints the TOC. The second prints the exact bytes the agent sees when
you run `prompt` — read mechanics, context-usage framing, any `ON_PROMPT.md`,
and your instruction.

## Next steps

- [Commands](commands.md) — the command catalog.
- [Cross-Project Sharing](cross-project-sharing.md) — symlink folders from other
  repos.
- [Reference](../reference/specification.md) — format specification.
