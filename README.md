# context-db

`context-db` is a project-knowledge layer for coding agents. The starting
picture is `AGENTS.md` or `CLAUDE.md` — a project's standing instructions for
the agent — but hierarchical instead of monolithic, re-loadable on demand
instead of only at session start, and bounded by a maintenance pass that keeps
it from bloating into what it was built to avoid. The four ideas:

- **Hierarchical Markdown, navigated on demand.** Every file and folder carries
  YAML `description` frontmatter (the same shape as a `SKILL.md`). A small
  Python script renders the table of contents for any folder at call time, so
  the agent walks a tree of descriptions and reads only the leaves it needs. By
  convention, 5–10 items per folder and ~150 lines per file: context loaded
  scales with the task, not with the size of the database.

- **Re-injection at decision points, not only at startup.** Standards loaded
  once at session start compact out of the agent's context on long sessions; by
  turn 40 the agent has drifted back to its training defaults.
  `/context-db prompt` re-fetches just the slice relevant to the next step — a
  deliberate moment where the user re-points the agent at the project's
  conventions, without having to remember which standards apply or where they
  live. `/context-db read` pulls in a whole area when the agent needs full
  coverage.

- **A bounded write loop.** `/context-db update` files what the agent learned —
  gotchas, decisions, conventions — using the same frontmatter and folder
  routing as hand-written entries, so the protocol that produces the database is
  the same one that grows it. `/context-db maintain` runs a multi-phase audit
  whose default posture is to **cut**: trim dead content, prune redundant
  entries, fix drift, reindex. Updates and maintenance balance each other so the
  database stays useful without bloating.

- **Global and local knowledge in one tree.** Symlink folders from a personal or
  team standards repo and they appear in the TOC alongside project-local content
  — coding standards, writing conventions, library runbooks, written once and
  used from every project.

## The commands

A single Python dispatcher exposes four commands. They take no configuration.

| Command               | What it does                                                 |
| --------------------- | ------------------------------------------------------------ |
| `prompt "<task>"`     | Re-inject the slice of context-db relevant to the next step. |
| `update "<learning>"` | File a learning into context-db (`--push` to commit + push). |
| `maintain [folder]`   | Multi-phase audit that keeps the database lean.              |
| `read [folder]`       | Read everything under a folder, exhaustively.                |

```bash
python3 .claude/skills/context-db/scripts/context-db-main-agent.py prompt "add a refund endpoint"
```

In Claude Code the dispatcher is packaged as the `/context-db` skill, so the
same call is just `/context-db prompt "add a refund endpoint"`.

## Typical folder structure

```
your-project/
├── AGENTS.md                              ← opt-in: tells the agent the commands exist
├── .claude/
│   └── skills/
│       └── context-db/                    ← the skill: commands + scripts
│           ├── SKILL.md
│           └── scripts/
│               ├── context-db-generate-toc.py
│               ├── context-db-main-agent.py
│               └── context-db-resolve-path.py
└── context-db/
    ├── ON_PROMPT.md                       ← optional: inlined on every prompt
    ├── ON_UPDATE.md                       ← optional: inlined on every update
    ├── ON_MAINTAIN.md                     ← optional: inlined on every maintain
    ├── <project-name>-project/            ← project-specific knowledge
    │   ├── <project-name>-project.md      ← folder description (frontmatter only)
    │   ├── architecture.md                ← document (frontmatter + body)
    │   └── data-model/
    ├── coding-standards/                  ← project-agnostic (often symlinked)
    └── writing-standards/                 ← project-agnostic (often symlinked)
```

By convention, the `<project-name>-project/` folder holds project-specific
knowledge. Folders parallel to it (like `coding-standards/`) are
project-agnostic and often symlinked from a shared standards repo.

## Wiring it in

context-db is **opt-in**. There is no startup hook and nothing fires on its own.
You reach it in one of two ways:

- **Invoke the commands directly** when you want them — by hand, or as the
  `/context-db` skill in Claude Code.
- **Make the agent aware of it** by pasting the shipped `AGENTS.md` boilerplate
  (`templates/AGENTS.md`) into your agent's standing-instructions file —
  `AGENTS.md`, `CLAUDE.md`, `.cursor/rules/`, or
  `.github/copilot-instructions.md`. The boilerplate tells the agent the
  knowledge base exists and — deliberately — that it must **not** read
  `context-db/` on its own; it engages only when you invoke a `/context-db`
  command.

The three optional `ON_*.md` files at the root of `context-db/` are the only
always-on mechanism: if present, each is inlined automatically when its matching
command runs. No configuration file, no globs.

## Why this design

Context files are often a net negative for coding agents.
[ETH Zurich research](https://www.infoq.com/news/2026/03/agents-context-file-value-review/)
found LLM-generated context files reduced task success by ~3% and increased cost
by 20%+; even hand-written ones showed only marginal gains. Agents trust the
file, read less of the actual code, and amplify any drift between description
and reality. Separately,
[Chroma's context-rot study](https://www.trychroma.com/research/context-rot)
showed every frontier model performs worse as input length grows, well below
context limits — so even correct context degrades the agent when there is too
much of it.

context-db's design follows from those two findings. Hierarchical Markdown plus
an on-demand TOC keeps the loaded slice small. Re-injection commands keep that
slice _fresh_ as the session grows. The `maintain` audit cuts content that no
longer earns its tokens. The litmus test for every entry: if you removed it,
would the agent make a mistake it wouldn't otherwise make? Anything that doesn't
clear that bar is, by the ETH Zurich finding, a _negative_-value document.

For the full treatment — including the negative result that motivated the
project — see
[Efficacy](https://cart0113.github.io/context-db/#/guide/efficacy).

## Getting started

1. **Create your context-db.** A `context-db/` directory at the repo root with a
   `<project-name>-project/` subfolder and a frontmatter-only descriptor.
2. **Install the dispatcher** at `.claude/skills/context-db/` — copy or symlink
   from `templates/skills/context-db/`. No config file needed.
3. **(Optional) Add the `ON_*.md` files** at the root of `context-db/` for rules
   the agent should see on every matching command.
4. **(Optional) Tell the agent the commands exist** by pasting
   `templates/AGENTS.md` into your agent's standing-instructions file. Or skip
   it and invoke the commands by hand.
5. **Verify** by running the TOC script and `prompt "test"` and reading the
   output.

Full walkthrough and per-agent paths:
[Getting Started](https://cart0113.github.io/context-db/#/guide/getting-started).

## Documentation

Full docs: <https://cart0113.github.io/context-db/>.

- [Commands](https://cart0113.github.io/context-db/#/guide/commands) — `prompt`,
  `update`, `maintain`, `read`.
- [CLI Reference](https://cart0113.github.io/context-db/#/reference/cli) — the
  literal `--help` and instruction text each command emits, generated from the
  dispatcher.
- [Reference](https://cart0113.github.io/context-db/#/reference/specification) —
  format specification.
- [Efficacy](https://cart0113.github.io/context-db/#/guide/efficacy) — research,
  test results, and the principles that keep context-db on the helpful side of
  the line.

## License

MIT
