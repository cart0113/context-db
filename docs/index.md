---
html_theme.sidebar_secondary.remove: true
---

# /context-db

:::{div} lead
A set of skills for coding agents. They keep a knowledge base for your project
as Markdown files in your repo, and tell the agent when to read it and when to
add to it.
:::

:::{div} okf-line
Built on the **Open Knowledge Format** (OKF), an open standard for knowledge
that agents can read.
[What OKF is, where it came from, and how context-db uses it](okf.md).
:::

## Example

Before a task, type the command, then the task on a new line. It needs no
quotes:

```text
/context-db prompt

Users report a bug here:

https://issues.example.com/PAY-482

It looks like it is in the new receipts database code.
Can you investigate and propose a fix?
```

The agent reads the index, opens the notes on the database schema and the plan
for the receipts work, and skips everything else. Then it finds the cause and
proposes a fix.

When the work is done:

```text
/context-db update --push
```

The agent writes down anything the next agent would need, then commits and
pushes. Most of the time there is nothing to write down, and it says so.

## Install

Paste this into your coding agent, in the project where you want it:

```text
Set up context-db in this repository. Follow the Install steps in the README at
https://github.com/cart0113/context-db
```

The agent copies the skills into your project, asks you a few questions, and
creates the knowledge base. [Setup](setup.md) has the same steps to run by hand.

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

## The four commands

::::{grid} 1 2 2 2
:gutter: 3

:::{grid-item-card} /context-db prompt
:class-card: command-card command-prompt
:link: commands
:link-type: doc

Run it before you start a task. The agent looks up what the knowledge base says
about that task.
:::

:::{grid-item-card} /context-db update
:class-card: command-card command-update
:link: commands
:link-type: doc

Run it when you finish. The agent writes down anything the next agent would
need. Add `--push` to commit and push as well.
:::

:::{grid-item-card} /context-db wip
:class-card: command-card command-wip
:link: commands
:link-type: doc

Optional. Keeps a short list of the work in progress, with a plan for each.
`--list` shows it, `--cleanup` deletes what has landed, `--clear` deletes it
all.
:::

:::{grid-item-card} /context-db configure
:class-card: command-card command-configure
:link: commands
:link-type: doc

A helper that sets things up by asking a few questions. Edit the files it
writes by hand afterwards.
:::
::::

Nothing is loaded when a session starts. The agent reads the knowledge base when
you run one of these commands. After `/context-db prompt` it may also add to it
as it works; `/context-db configure` asks whether you want that.

Each command gives the agent a set of instructions, so that you do not have to
type them every time. You add your own rules in a few plain Markdown files and
edit them by hand. `/context-db configure` is a helper that writes a first
version of them by asking you a few questions.

## What the knowledge base looks like

::::{tab-set}

:::{tab-item} The folder
```text
context-db/
├── configuration/               settings and rules, all plain Markdown
├── acme-payments-project/       the project folder: your project's knowledge
│   ├── index.md                 generated list of everything in this folder
│   ├── architecture.md
│   ├── pci-handling.md
│   ├── data-model/
│   └── wip/                     optional: wip.md lists the work in progress
└── coding-standards/            a background folder shared with other projects
```
:::

:::{tab-item} A file
```markdown
---
type: Decision
description:
  Why refunds are processed asynchronously, and the idempotency-key rule that
  follows from it
---

# Asynchronous refunds

Refunds go through the ledger queue. Never process one inline: a retry after a
timeout would refund the customer twice.

Every refund request carries an idempotency key. See
[the capture flow](./architecture.md) for the scheme.
```
:::

:::{tab-item} An index
```markdown
# Subfolders

* [data-model](data-model/index.md) - Database schema — the payment, refund, and merchant entities
* [wip](wip/index.md) - Work in progress, if the project records it

# Files

* [API Reference](api-reference.md) - The REST API — authentication and the payments and refunds endpoints
* [Architecture](architecture.md) - The three services, what each one owns, and how they talk
* [PCI handling](pci-handling.md) - What may never be stored or logged, and what needs a security review
```
:::
::::

## Motivation

On a large project that runs for months, every agent session starts knowing
nothing. It has to rediscover the conventions, the decisions already made and
why, the mistakes from last time, and where the current work stands.
context-db is an explicit memory for that: a folder of short notes in your
repository that you and the agent keep up as the project goes, and that the
agent reads when you ask it to.

The idea comes from Andrej Karpathy's
[LLM wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f):
have the LLM keep a wiki of what it has learned, instead of working everything
out again each time.
context-db uses that idea to cut down how much context has to be loaded for
each task, which keeps the agent focused and efficient.

The usual answer is a big `AGENTS.md` or `CLAUDE.md`. That file is loaded into
every session in full, whatever the task, and as it grows the problems are well
known. Most of it has nothing to do with the task at hand, and the part that
matters gets lost in the rest. The agent trusts it and reads less of the code.
Nobody notices when it goes out of date, so the agent repeats what it gets
wrong. Rules read at the start of a long session have faded by the time the
work they apply to comes up.

context-db hands the agent small pieces of text at set points in the work
instead:

- `prompt`, right before a task: the index of the knowledge base, the plans for
  the work in progress, and your rules. The agent opens only the notes that
  match the task.
- `update`, after a task: what belongs in the knowledge base and what does not,
  so that it stays small.
- `wip`, during long work: how to keep a short record of where things stand.

The rest stays out of the agent's context. Where a note and the code disagree,
the agent is told to trust the code and tell you.

Keep it small. If deleting a note would not make the agent do anything wrong,
delete it.

```{toctree}
:hidden:

Setup <setup>
Commands <commands>
Layout <layout>
OKF <okf>
```
