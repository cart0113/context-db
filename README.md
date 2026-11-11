# context-db

A set of skills for coding agents. They keep a knowledge base for your project
as Markdown files in your repo, and tell the agent when to read it and when to
add to it.

**Built on the [Open Knowledge Format](https://github.com/GoogleCloudPlatform/open-knowledge-format)
(OKF)**, an open standard for knowledge that agents can read. OKF grew out of
Andrej Karpathy's
[LLM wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
idea.
[What OKF is, where it came from, and how context-db uses it](https://cart0113.github.io/context-db/okf.html).

Documentation: <https://cart0113.github.io/context-db/>

## What it is

context-db is a set of skills that you install in a coding agent such as Claude
Code. They come as one folder and show up as four commands under `/context-db`.

The commands work on a folder in your repository called `context-db/`. That
folder is the knowledge base. It holds what an agent cannot work out by reading
your code: your conventions, the decisions you made and why, the mistakes to
avoid, and the plan for the work in progress.

Everything in it is a Markdown file with a short description at the top. Every
folder has an `index.md` that lists what is inside, one line each. The agent
reads the index, opens the one or two files it needs, and leaves the rest alone.

There is no database and no server, in spite of the name. It is a folder of text
files and one Python script.

```
your-project/
├── .claude/skills/context-db/      the skills: SKILL.md, context-db.py, prompts/
└── context-db/
    ├── context-db.json             settings
    ├── context-db-on-markdown/     rules the agent sees on every command
    ├── acme-payments-project/      the project folder: your project's knowledge
    │   ├── index.md                generated list of everything in this folder
    │   ├── architecture.md
    │   ├── data-model/
    │   └── wip/                    plans for the work in progress
    └── coding-standards/           a background folder shared with other projects
```

## The four commands

| Command | When to run it | What the agent does |
| --- | --- | --- |
| `/context-db prompt "<task>"` | Before a task | Looks up what the knowledge base says about the task. |
| `/context-db update` | After a task | Writes down anything the next agent would need. `--push` also commits and pushes. |
| `/context-db wip "<what you are doing>"` | During long work | Keeps a short plan of the work in progress, and deletes plans for work that has landed. |
| `/context-db configure` | Once per repository | Sets everything up. |

Nothing runs by itself. The agent reads or writes the knowledge base only when
you run one of these commands.

Each command gives the agent a set of instructions, so that you do not have to
type them every time. You control those instructions with a few rule files in
`context-db/context-db-on-markdown/`, and `/context-db configure` edits them for
you: it asks what you want and writes it down.

Outside Claude Code, run the same commands from a terminal:

```bash
python3 .claude/skills/context-db/context-db.py prompt "add a refund endpoint"
```

## A typical session

1. You type `/context-db prompt "add a refund endpoint"`.
2. The agent reads the index, opens the notes on the payments API and the plan
   for refunds, and skips everything else.
3. It writes the code.
4. You type `/context-db update --push`. The agent asks itself whether it
   learned anything that the next agent would get wrong without being told.
   Usually the answer is no, and it says so. If there is something, it writes a
   short note in the right place. Then it commits and pushes.

## Install

You need Python 3.8 or newer.

```bash
git clone -b v0.1 https://github.com/cart0113/context-db /tmp/context-db
mkdir -p .claude/skills
cp -r /tmp/context-db/skill/context-db .claude/skills/
```

Then type `/context-db configure` in Claude Code, or run:

```bash
python3 .claude/skills/context-db/context-db.py init --project <name>
```

[Get started](https://cart0113.github.io/context-db/getting-started.html) has
the full steps. If you are on v0.0, see
[Migrating](https://cart0113.github.io/context-db/migrating.html).

## Why use it

Agents lose track of a project's rules partway through a long session, and they
never knew the reasons behind your code in the first place. One large
instructions file does not fix this.
[Research from ETH Zurich](https://www.infoq.com/news/2026/03/agents-context-file-value-review/)
found that context files often make agents perform worse: the agent follows the
file and reads less of the code.

A small knowledge base that the agent reads a little at a time, and only when
asked, does better.
[Why it works this way](https://cart0113.github.io/context-db/why.html) has the
details.

## Documentation

- [Get started](https://cart0113.github.io/context-db/getting-started.html)
- [Commands](https://cart0113.github.io/context-db/commands.html), with the
  exact text each one gives the agent
- [The knowledge base](https://cart0113.github.io/context-db/knowledge-base.html):
  what goes where, and what a file looks like
- [The Open Knowledge Format](https://cart0113.github.io/context-db/okf.html):
  what it is and which parts context-db uses
- [Sharing knowledge between projects](https://cart0113.github.io/context-db/background-folders.html)
- [Why it works this way](https://cart0113.github.io/context-db/why.html)

## Working on context-db itself

```bash
python3 -m venv .venv
.venv/bin/pip install pytest pyyaml ruff -r docs/requirements.txt
.venv/bin/python -m pytest tests
.venv/bin/sphinx-build -W docs docs/_build/html
cp hooks/pre-commit .git/hooks/pre-commit
```

The docs are Markdown files in `docs/`, built with Sphinx and the PyData theme.
This repository uses its own skills on its own `context-db/` folder.

## License

MIT
