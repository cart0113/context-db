# Setup

You need Python 3.8 or newer, and a coding agent that can run shell commands.
These steps use Claude Code.

## Ask your agent to do it

Open your project in your agent and paste this:

```text
Set up context-db in this repository. Follow the Install steps in the README at
https://github.com/cart0113/context-db
```

The agent copies the skills into your project, asks you a few questions as a
menu, and creates the knowledge base. That covers steps 1, 2, and 4 below. Read
on to do them by hand, or to see what the agent did.

## 1. Copy the skills into your project

```bash
git clone -b v0.1 https://github.com/cart0113/context-db /tmp/context-db
mkdir -p .claude/skills
cp -r /tmp/context-db/skill/context-db .claude/skills/
```

The skills come as one folder: a Python script, a few instruction files, and
some starter templates. Commit it with your project so that everyone on the team
has the same version.

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

The agent asks a few questions as a menu, then creates the folders. The main
question is who updates the knowledge base:

- **Only when you run `/context-db update`.** Nothing is written unless you ask.
  This is the default.
- **Also when the agent thinks it should.** The agent writes down what it learns
  as it goes, and tells you each time. It never commits on its own.

To do the same by hand:

```bash
python3 .claude/skills/context-db/context-db.py init --project acme-payments
```

Either way you end up with this:

```text
context-db/
├── configuration/
│   ├── settings.md
│   ├── ON_PROMPT.md
│   ├── ON_UPDATE.md
│   ├── ON_WIP.md
│   └── ON_CONFIGURE.md
└── acme-payments-project/
    ├── acme-payments-project.md
    ├── index.md
    └── wip/
        └── wip.md
```

Running it again is safe. It never overwrites a file that already exists.

## 3. Make it behave the way you want

Four files in `context-db/configuration/` control how the agent behaves:
`ON_PROMPT.md`, `ON_UPDATE.md`, `ON_WIP.md`, and `ON_CONFIGURE.md`. Whatever a
file says is added to the agent's instructions every time that command runs.

Open them and edit them by hand. They are plain Markdown, and the agent reads
exactly what they say. `/context-db configure` is a helper that wrote the first
version; run it again if you would rather answer questions than edit.

[Commands](commands.md) has examples of rules.

## 4. Tell the agent to leave it alone

Add the text in `.claude/skills/context-db/starters/AGENTS.md` to your
`AGENTS.md` or `CLAUDE.md`.

It tells the agent that the knowledge base exists, and that it should not read
it unless you run a command. `configure` offers to add it for you. This matters. An agent that loads the whole
knowledge base at the start of every session has less attention left for your
task. [Motivation](index.md#motivation) covers the
research.

## 5. Use it

Before a task, type the command, then the task on a new line. It needs no
quotes:

```text
/context-db prompt

Add an endpoint for refunds. Partial refunds can wait.
```

After it:

```text
/context-db update --push
```

That is the whole loop: `prompt`, work for as many turns as it takes, `update
--push`. For work that runs over several sessions, you can also keep a
record with `/context-db wip`; it is optional. [Commands](commands.md) explains all four.

## Settings

Settings live in `context-db/configuration/settings.md`, which is committed, so
the whole team shares it. They are the `key: value` lines at the top:

```markdown
---
project: acme-payments
python: python3
main_branch: main
---
```

| Setting | Meaning |
| --- | --- |
| `project` | The project's name. The project folder is `context-db/<project>-project/`. |
| `python` | The command the agent uses to run the script. |
| `main_branch` | The branch that `wip --cleanup` compares your current branch against. |

Edit them by hand. Anything below the `---` lines is yours for notes.

`context-db/configuration/settings.local.md` is yours alone. It is gitignored,
and anything in it overrides the shared file. Use it when your machine needs
something different, such as a Python that lives in an unusual place:

```bash
python3 .claude/skills/context-db/context-db.py init --local python=/opt/python3.12/bin/python3
```

## Check it in CI

This command changes nothing. It exits with an error if an `index.md` is out of
date or a file breaks the [format](layout.md):

```bash
python3 .claude/skills/context-db/context-db.py index --check
```

Add it to a pre-commit hook or a CI job.

## See a complete example

The repository has a small, working project in
[`example/`](https://github.com/cart0113/context-db/tree/v0.1/example).
