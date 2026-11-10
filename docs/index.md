# context-db

**An [Open Knowledge Format](https://github.com/GoogleCloudPlatform/open-knowledge-format)
bundle that lives in your repo, plus four commands that tell a coding agent when
to read it and when to write it.**

The knowledge base is a hierarchical Markdown wiki. Every folder has a generated
`index.md` with one described line per child, so an agent reads a short list,
follows the one link it needs, and never loads the rest.

```text
context-db/
├── context-db.json                 config written by `configure`
├── context-db-on-markdown/         rules inlined on every command
├── acme-payments-project/          the project bundle — commands write here
│   ├── index.md                    generated
│   ├── architecture.md
│   ├── data-model/
│   └── wip/                        what is being built right now
└── coding-standards -> ...         a background bundle — read-only
```

## The four commands

| Command                 | What it does                                              |
| ----------------------- | --------------------------------------------------------- |
| `prompt "<task>"`       | Re-centers the agent on the knowledge relevant to a task. |
| `update ["<learning>"]` | Files a learning. `--push` also commits and pushes.       |
| `wip ["<instruction>"]` | Refreshes the plan for current work and deletes what landed. |
| `configure`             | Creates or repairs the config and scaffolding.            |

Nothing runs on its own. There is no startup hook and no sub-agent. Each command
prints instructions and the agent follows them.

## The ideas

Format is OKF; operations are context-db.
: OKF says what the files look like. context-db says when a coding agent reads
  them and what is worth writing. See [](format.md).

Re-inject at the moment of work.
: Standards loaded at session start are compacted away on a long session.
  `prompt` fetches the relevant slice immediately before the work it applies to.

Most sessions store nothing.
: `update` opens by asking whether the next agent would get something wrong
  without this knowledge. Usually the answer is no. See [](why.md).

One project bundle, any number of background bundles.
: Project knowledge lives in `<name>-project/`. Shared standards are mounted
  beside it and never edited. See [](background-bundles.md).

```{toctree}
:hidden:
:maxdepth: 2

getting-started
commands
format
background-bundles
why
migrating
```
