# context-db

**An [Open Knowledge Format](https://github.com/GoogleCloudPlatform/open-knowledge-format)
bundle that lives in your repo, plus four commands that tell a coding agent when
to read it and when to write it.**

The knowledge base is a hierarchical Markdown wiki. Every folder has a generated
`index.md` with one described line per child, so an agent reads a short list,
follows the one link it needs, and never loads the rest. No sub-agents, no
hooks, no dependencies: one Python script and a few prompt files.

```
your-project/
├── AGENTS.md                         opt-in: tells the agent the commands exist
├── .claude/skills/context-db/        the skill: SKILL.md, context-db.py, prompts/
└── context-db/
    ├── context-db.json               config written by `configure`
    ├── context-db-on-markdown/       ON_PROMPT.md, ON_UPDATE.md, ON_WIP.md, ON_CONFIGURE.md
    ├── <name>-project/               the project bundle — the only place commands write
    │   ├── index.md                  generated
    │   ├── <name>-project.md         folder descriptor
    │   ├── architecture.md
    │   ├── data-model/
    │   └── wip/                      what is being built right now
    └── coding-standards -> ...       a background bundle — read-only
```

## The commands

| Command                 | What it does                                                 |
| ----------------------- | ------------------------------------------------------------ |
| `prompt "<task>"`       | Re-centers the agent on the knowledge relevant to a task.    |
| `update ["<learning>"]` | Files a learning. `--commit` or `--push` commits the session. |
| `wip ["<instruction>"]` | Refreshes the plan for current work and deletes what landed. |
| `configure`             | Creates or repairs the config and scaffolding.               |

In Claude Code these are `/context-db prompt "add a refund endpoint"` and so on.
Anywhere else, run the script:

```bash
python3 .claude/skills/context-db/context-db.py prompt "add a refund endpoint"
```

Each command prints instructions and the agent follows them. Nothing runs on its
own.

The everyday loop is two commands: `prompt` before a piece of work, and
`update --push` after it.

## The ideas

- **OKF for the format, context-db for the operations.** Every file has YAML
  frontmatter with a `type` and a `description`. Every bundle is a conformant
  OKF v0.2 bundle that Obsidian, GitHub, and OKF tools can read. What OKF does
  not define is when an agent should read or write, and that is what the
  commands add.

- **Re-inject at the moment of work.** Standards loaded at session start are
  compacted away on a long session. `prompt` fetches the relevant slice
  immediately before the work it applies to.

- **Most sessions store nothing.** `update` opens by asking whether the next
  agent would get something wrong without this knowledge. Usually the answer is
  no, and the agent says so and stops.

- **Work in progress has its own place.** `<name>-project/wip/` holds the plans
  for what is being built right now. `prompt` lists them every time. `wip`
  compares them against git and deletes what has landed.

- **One project bundle, any number of background bundles.** Project-specific
  knowledge lives in `<name>-project/`. Shared standards and reference material
  are mounted beside it, usually as symlinks to another repo, and are never
  edited from here.

## Getting started

```bash
git clone -b v0.1 https://github.com/cart0113/context-db /tmp/context-db
mkdir -p .claude/skills
cp -r /tmp/context-db/skill/context-db .claude/skills/context-db
python3 .claude/skills/context-db/context-db.py init --project <name>
```

Or, in Claude Code, run `/context-db configure` after copying the skill and let
the agent do the rest. Then paste `.claude/skills/context-db/starters/AGENTS.md`
into your `AGENTS.md` or `CLAUDE.md`.

Requires Python 3.8 or newer. Coming from v0.0? See
[Migrating](https://cart0113.github.io/context-db/migrating.html).

## Config

`context-db/context-db.json` is committed and shared:

```json
{
  "project": "acme-payments",
  "python": "python3",
  "main_branch": "main"
}
```

`context-db/context-db.local.json` is gitignored, and any key in it overrides
the shared value for one user. Use it for an interpreter path that exists only
on one machine.

## Why this design

[ETH Zurich research](https://www.infoq.com/news/2026/03/agents-context-file-value-review/)
found LLM-generated context files reduced task success by about 3% and increased
cost by more than 20%.
[Chroma's context-rot study](https://www.trychroma.com/research/context-rot)
showed every frontier model performing worse as input grows. Agents trust a
context file, read less of the actual code, and amplify any drift between the
two.

So the index keeps the loaded slice small, `prompt` keeps it fresh, and `update`
is biased toward writing nothing. The test for every entry: if it were removed,
would the agent make a mistake it would not otherwise make?

## Documentation

<https://cart0113.github.io/context-db/>

- [Getting started](https://cart0113.github.io/context-db/getting-started.html)
- [Commands](https://cart0113.github.io/context-db/commands.html) — including
  the exact instruction text each one prints
- [Format](https://cart0113.github.io/context-db/format.html) — the OKF profile
- [Background bundles](https://cart0113.github.io/context-db/background-bundles.html)
- [Why it works this way](https://cart0113.github.io/context-db/why.html)

## Developing

```bash
python3 -m venv .venv && .venv/bin/pip install pytest ruff -r docs/requirements.txt
.venv/bin/python -m pytest tests
.venv/bin/sphinx-build -W docs docs/_build/html
cp hooks/pre-commit .git/hooks/pre-commit
```

The repo uses its own skill on its own `context-db/`.

## License

MIT
