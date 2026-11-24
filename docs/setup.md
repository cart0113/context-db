# Setup

You need Python 3.8 or newer, and a coding agent that can run shell commands.
These steps use Claude Code, which reads skills from `.claude/skills/`.

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
skills, such as `.codex/skills/` for Codex, and use that path in the commands
below. You can also run any command yourself from a terminal:

```bash
python3 .claude/skills/context-db/context-db.py --help
```

To have a `context-db` command instead, install the repository with
`pip install .`. It runs the same script, and the commands it prints for the agent
use that name, as it was invoked.

## 2. Set it up

In Claude Code, type:

```text
/context-db configure
```

Other agents invoke a skill their own way, or you can ask the agent in plain
words to run the context-db `configure` command.

This is the first thing to run. The agent asks for the project name and creates
the folders. Then it asks a few questions as a menu about how it should treat
the knowledge base: whether breaking changes are fine in this project, whether
to read the knowledge base only when you run a command, whether to update it as
it works, and when to split files that grow too long. [Commands](commands.md)
lists them all.

To set it up with no questions:

```bash
python3 .claude/skills/context-db/context-db.py configure --project acme-payments
```

Either way you end up with this:

```text
context-db/
├── configuration/
│   ├── settings.md
│   ├── ON_PROMPT.md
│   ├── ON_UPDATE.md
│   ├── ON_WIP.md
│   ├── ON_CONFIGURE.md
│   └── ON_MAINTAIN.md
└── acme-payments-project/
    ├── acme-payments-project.md
    └── wip/
        └── wip.md
```

Running it again is safe. It never overwrites a file that already exists.

## 3. Make it behave the way you want

Five files in `context-db/configuration/` control how the agent behaves:
`ON_PROMPT.md`, `ON_UPDATE.md`, `ON_WIP.md`, `ON_MAINTAIN.md`, and
`ON_CONFIGURE.md`. Whatever a file says is added to the agent's instructions
every time that command runs.

Open them and edit them by hand. They are plain Markdown, and the agent reads
exactly what they say. `/context-db configure` is a helper that wrote the first
version; run it again if you would rather answer questions than edit.

Those five hold the project's rules, and everyone on the project gets them.
Rules that are only yours go in a file of the same name ending in `.local.md`,
such as `ON_PROMPT.local.md`. It is added after the project's file, and it is
gitignored.

[Commands](commands.md#rule-files) has examples of rules.

## 4. Tell the agent to leave it alone

Add the text in `starters/AGENTS.md`, in the skill folder, to your
`AGENTS.md` or `CLAUDE.md`.

It tells the agent that the knowledge base exists, and that it should not read
it unless you run a command. `configure` offers to add it for you. This
matters. An agent that loads the whole knowledge base at the start of every
session has less attention left for your task.

## 5. Use it

Before a task, type the command, then the task on a new line. It needs no
quotes:

```text
/context-db prompt

Add an endpoint for refunds. Partial refunds can wait.
```

After it:

```text
/context-db update
```

That is the whole loop: `prompt`, work for as many turns as it takes,
`update`. If you like, `update` can also
[commit and push](commands.md#context-db-update) what the session changed.
For work that runs over several sessions, you can also keep a plan with
`/context-db wip`; it is optional. `prompt` then starts the next session on
that work from the plan, and `update` keeps it up to date. Run
`/context-db maintain` rarely, as a spring cleaning, to cut the knowledge base
back to what is still needed. [Commands](commands.md) explains all five.

Each command is a starting point. It covers the whole knowledge base, and
there are no flags to narrow it. When you want something narrower or
different, say so in plain words after the command.
[A command is a starting point](commands.md#a-command-is-a-starting-point)
has examples.

## Where the knowledge is

By default context-db looks for knowledge in one place: the `context-db/`
folder at the top of your repository.

```text
context-db/
├── configuration/               settings and rules
├── acme-payments-project/       your project's own knowledge
│   └── acme-payments-usage/     what other projects need to use yours (optional)
├── coding-standards/            knowledge from elsewhere, copied in
└── acme-ledger-usage -> ...     knowledge from elsewhere, symlinked in
```

- `context-db/<name>-project/` is the project folder. It holds the knowledge
  that is your project's own, and it is the only folder here that the commands
  write. If other projects use yours, tell `update` to start a
  [usage folder](layout.md#usage-folders) inside it.
- Every other folder in `context-db/` is knowledge from somewhere else, such
  as your team's coding standards, or the usage folder of a project that yours
  uses. Copy the folder in, or symlink it into place. The agent reads it and
  never changes it. [Sharing](layout.md#sharing) shows both ways.

`prompt` lists each of these folders with its description, your project folder
first, and the agent looks into the ones that match the task.

## Knowledge kept somewhere else

Knowledge does not have to be inside `context-db/`. The `global_context`
setting finds knowledge folders where they are, with nothing copied or linked:

```yaml
---
project: acme-payments
python: python3
main_branch: main
global_context:
  - okf/*-usage
  - ../*/okf/*-usage
---
```

Each value is a glob pattern, read from the top of your repository. The first
one here matches every folder whose name ends in `-usage` in your own `okf/`
folder. The second matches the same in each repository checked out next to
yours. `prompt` lists the folders they match after your own, and the agent
never changes them. [Global context](layout.md#global-context) has more.

Your own usage folder can live outside `context-db/` as well, for a team that
publishes it from a folder such as `okf/`. The `usage_folders` setting says
where. [Keeping it somewhere else](layout.md#keeping-it-somewhere-else) has
more.

## Settings

The settings are the `key: value` lines at the top of
`context-db/configuration/settings.md`. The file is committed, so the whole
team shares it. This one uses every setting:

```yaml
---
project: acme-payments
python: python3
main_branch: main
usage_folders: okf/acme-payments-usage
global_context:
  - okf/*-usage
  - ../*/okf/*-usage
settings_files: ../standards/context-db-settings.md
---
```

| Setting | What it is |
| --- | --- |
| `project` | The project's name. The project folder is `context-db/<project>-project/`. |
| `python` | The command the agent uses to run the script. |
| `main_branch` | The branch that the plans in `wip/` are checked against. |
| `usage_folders` | Optional. Where your [usage folders](layout.md#usage-folders) are kept. Left out, there is one, inside the project folder. `{project}` in a path stands for the project name. |
| `global_context` | Optional. Patterns that find [knowledge kept somewhere else](#knowledge-kept-somewhere-else). |
| `settings_files` | Optional. [More settings files](#settings-from-other-files), read after this one. |

`configure` writes the first three. Add the others by hand, or with
`configure --usage-folder` and `configure --global-context`.

The last three take one value on the line, or several as a list, the way
`global_context` is written above. Paths and patterns are read from the top of
your repository, and can also start with `~` or `/`.

Anything below the `---` lines is yours for notes. The commands stop on a line
that is not a setting, so that a misspelt name is not ignored without a word.

### Your own settings

`context-db/configuration/settings.local.md` is yours alone. It is gitignored,
like every `*.local.md` file in that folder, and anything in it overrides the
shared file. Use it when your machine needs something different, such as a
Python that lives in an unusual place:

```bash
python3 .claude/skills/context-db/context-db.py configure --local python=/opt/python3.12/bin/python3
```

### Settings from other files

`settings_files` names more settings files. You write them yourself, and they
can live anywhere: in a repository your team shares, or in your home folder.
Each looks like `settings.md`, and is read after the file that names it, so
what it sets wins.

This one is shared by a team that keeps every project's usage folder in `okf/`,
and finds the others there:

```yaml
---
usage_folders: okf/{project}-usage
global_context:
  - okf/*-usage
  - ../*/okf/*-usage
---
```

With that file, each project writes its own usage notes to `okf/<name>-usage/`,
and reads the usage folders of the repositories checked out next to it.

The files are read in this order. A later one overrides an earlier one, setting
by setting:

1. `settings.md`
2. the files that `settings.md` names
3. `settings.local.md`
4. the files that `settings.local.md` names

So name a file that everyone on the project has in `settings.md`, and a file
that only you have in `settings.local.md`. Your own settings still win over the
team's.

No command writes these files, or the `settings_files` line. If a file named
there is missing or has no `---` block, the commands stop and say which file it
is. `/context-db configure` still runs, and lists every settings file in the
order it is read.

Keep `python` in `settings.md` or `settings.local.md`. The agent reads that one
line itself, from those two files, before it can run the script.

## Check it in CI

This command changes nothing. It exits with an error if a file breaks the
[format](layout.md):

```bash
python3 .claude/skills/context-db/context-db.py toc --check
```

Add it to a pre-commit hook or a CI job.

## See a complete example

The repository has a small, working project in
[`example/`](https://github.com/cart0113/context-db/tree/v0.1/example).
