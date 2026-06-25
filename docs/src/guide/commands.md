# Commands

context-db's behavior is exposed as sub-commands on a single dispatcher script:

```bash
python3 .claude/skills/context-db/scripts/context-db-main-agent.py <command> [args]
```

There are four commands and no configuration file. This page describes each at
the level of "what would I use this for." For the literal `--help` output and
the verbatim instruction text each command emits to the agent, see the
[CLI reference](../reference/cli.md) — it is generated from the dispatcher and
the prompt templates so it cannot drift.

Multi-word instructions must be quoted as a single shell argument. The script
runs in any terminal; most agents wrap it for ergonomics — see
[Per-agent invocation](#per-agent-invocation).

## `prompt <instruction>`

Re-inject context relevant to a specific piece of work. Use it when the agent
should ground its next step in project knowledge before answering or coding. The
dispatcher prints the read mechanics (how to navigate the TOC), the
context-usage framing, and your instruction; the agent then walks context-db and
pulls in just the topical material the task needs. Adding `--use-git-diff`
surfaces context-db files touched recently, first.

```
prompt "How do I add a new payment endpoint?"
prompt --use-git-diff "Pick up where the last session left off"
```

If `context-db/ON_PROMPT.md` exists, it is inlined automatically on every
`prompt` call.

## `update <what was learned>`

Files learnings into context-db — gotchas, convention decisions, surprises. The
agent picks the right home (defaulting to the project folder), updates
frontmatter descriptions, and re-runs the TOC where needed. Add `--commit` to
commit the affected files, or `--push` to commit and push, in the same call.

```
update "Polling Linear webhooks doesn't deliver retries"
update --push "Same, and ship it"
```

If `context-db/ON_UPDATE.md` exists, it is inlined automatically on every
`update` call.

## `maintain [folder]`

Multi-phase audit that keeps context-db from bloating into what it was built to
avoid: structural health, content freshness, content value, coverage gaps, doc
drift, cross-references, reindex. Default posture is to **cut**. An optional
folder argument scopes the audit.

If `context-db/ON_MAINTAIN.md` exists, it is inlined automatically on every
`maintain` call.

## `read [folder]`

Instructs the agent to read a context-db folder exhaustively — every file, every
subfolder, all the way down — rather than selectively by relevance. Use it when
the agent needs full coverage of an area (e.g. before a large change). Defaults
to the whole `context-db/` tree if no folder is given.

```
read
read context-db/acme-payments-project/data-model/
```

## The `ON_*.md` special files

Three optional files at the root of `context-db/` are the only always-on
mechanism — no config, fixed names:

| File                        | Inlined on       |
| --------------------------- | ---------------- |
| `context-db/ON_PROMPT.md`   | every `prompt`   |
| `context-db/ON_UPDATE.md`   | every `update`   |
| `context-db/ON_MAINTAIN.md` | every `maintain` |

If a file exists, its body is inlined raw (frontmatter stripped) when its
command runs. Use them for the handful of rules the agent should see every time.
Keep them brief — every line is re-read on every matching call.

In practice `ON_PROMPT.md` is the only one most projects ever use — `prompt` is
the command an agent runs constantly, and that is where standing rules earn
their keep. `ON_UPDATE.md` and `ON_MAINTAIN.md` work identically but are rarely
needed. A worked example to copy lives at `templates/ON_PROMPT.md`.

## Per-agent invocation

The underlying script call is identical across agents. Each one has its own
ergonomic wrapper.

### Claude Code

The dispatcher is packaged as the `/context-db` skill, so commands run as:

```
/context-db prompt "..."
/context-db update --push "..."
```

The skill's `SKILL.md` quotes the user's instruction correctly and forwards
everything to the dispatcher.

### Cursor

No native skill system, so the simplest path is to call the script directly from
chat with the terminal tool, or define a shell alias:

```bash
alias cdb='python3 .claude/skills/context-db/scripts/context-db-main-agent.py'
cdb prompt "..."
```

A project-level `.cursor/rules/` file can document the alias so the agent uses
it consistently.

### Codex / generic

The agent runs the script directly via its shell tool, exactly as shown at the
top of this page. No wrapper required.
