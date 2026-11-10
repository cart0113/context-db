# Get started

You need Python 3.8 or newer, and a coding agent that can run shell commands.
These steps use Claude Code.

## 1. Copy the skill into your project

```bash
git clone -b v0.1 https://github.com/cart0113/context-db /tmp/context-db
mkdir -p .claude/skills
cp -r /tmp/context-db/skill/context-db .claude/skills/
```

The skill is one folder: a Python script, a few instruction files, and some
starter templates. Commit it with your project so that everyone on the team has
the same version.

If you use a different agent, put the folder wherever that agent keeps its
skills. You can also run any command yourself from a terminal:

```bash
python3 .claude/skills/context-db/context-db.py help
```

## 2. Set it up

In Claude Code, type:

```text
/context-db configure
```

The agent suggests a project name, checks which Python to use, and creates the
folders. It asks you about anything it is unsure of.

To do the same by hand:

```bash
python3 .claude/skills/context-db/context-db.py init --project acme-payments
```

Either way you end up with this:

```text
context-db/
├── context-db.json
├── context-db-on-markdown/
│   ├── ON_PROMPT.md
│   ├── ON_UPDATE.md
│   ├── ON_WIP.md
│   └── ON_CONFIGURE.md
└── acme-payments-project/
    ├── acme-payments-project.md
    ├── index.md
    └── wip/
```

Running it again is safe. It never overwrites a file that already exists.

## 3. Tell the agent to leave it alone

Add the text in `.claude/skills/context-db/starters/AGENTS.md` to your
`AGENTS.md` or `CLAUDE.md`.

It tells the agent that the knowledge base exists, and that it should not read
it unless you run a command. This matters. An agent that loads the whole
knowledge base at the start of every session has less attention left for your
task. [Why it works this way](why.md) covers the research.

## 4. Use it

Before a task:

```text
/context-db prompt "add a refund endpoint"
```

After it:

```text
/context-db update --push
```

That is the whole loop. For work that runs over several sessions, start with
`/context-db wip`. [Commands](commands.md) explains all four.

## Settings

Settings live in two files.

`context-db/context-db.json` is committed, so the whole team shares it:

```json
{
  "project": "acme-payments",
  "python": "python3",
  "main_branch": "main"
}
```

| Setting | Meaning |
| --- | --- |
| `project` | The project's name. The project folder is `context-db/<project>-project/`. |
| `python` | The command the agent uses to run the script. |
| `main_branch` | The branch that `wip` compares your current branch against. |

`context-db/context-db.local.json` is yours alone. It is gitignored, and
anything in it overrides the shared file. Use it when your machine needs
something different, such as a Python that lives in an unusual place:

```bash
python3 .claude/skills/context-db/context-db.py init --local python=/opt/python3.12/bin/python3
```

## Check it in CI

This command changes nothing. It exits with an error if an `index.md` is out of
date or a file breaks the [format](knowledge-base.md):

```bash
python3 .claude/skills/context-db/context-db.py index --check
```

Add it to a pre-commit hook or a CI job.

## See a complete example

The repository has a small, working project in
[`example/`](https://github.com/cart0113/context-db/tree/v0.1/example).
