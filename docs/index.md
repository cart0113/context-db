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
that agents can read. It grew out of Andrej Karpathy's LLM wiki idea.
[What OKF is, where it came from, and how context-db uses it](okf.md).
:::

::::{div} hero-buttons
```{button-ref} setup
:color: primary
:class: hero-button

Setup
```
```{button-ref} okf
:color: secondary
:outline:
:class: hero-button

About the Open Knowledge Format
```
::::

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

Keeps a short plan of the work in progress, and deletes plans for work that has
landed.
:::

:::{grid-item-card} /context-db configure
:class-card: command-card command-configure
:link: commands
:link-type: doc

Sets everything up. You run it once per repository.
:::
::::

Nothing runs by itself. The agent reads or writes the knowledge base only when
you run one of these commands.

Each command gives the agent a set of instructions, so that you do not have to
type them every time. You control those instructions with a few rule files, and
`/context-db configure` edits them for you: it asks what you want and writes it
down.

## What the knowledge base looks like

::::{tab-set}

:::{tab-item} The folder
```text
context-db/
├── context-db.json              settings
├── context-db-on-markdown/      rules the agent sees on every command
├── acme-payments-project/       the project folder: your project's knowledge
│   ├── index.md                 generated list of everything in this folder
│   ├── architecture.md
│   ├── pci-handling.md
│   ├── data-model/
│   └── wip/                     plans for the work in progress
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
* [wip](wip/index.md) - Plans for what is being built right now

# Files

* [API Reference](api-reference.md) - The REST API — authentication and the payments and refunds endpoints
* [Architecture](architecture.md) - The three services, what each one owns, and how they talk
* [PCI handling](pci-handling.md) - What may never be stored or logged, and what needs a security review
```
:::
::::

## Why it works this way

Notes about a project can make an agent worse.
[Researchers at ETH Zurich](https://www.infoq.com/news/2026/03/agents-context-file-value-review/)
found that context files written by an LLM lowered the success rate by about 3%
and raised cost by more than 20%. Files written by people helped only a little.
[Chroma](https://www.trychroma.com/research/context-rot) found that every model
it tested did worse as its input grew. An agent that is handed a file about the
project trusts it, reads less of the code, and repeats whatever the file gets
wrong.

context-db is built around that:

- Nothing is loaded when a session starts. The agent reads the knowledge base
  only when you run a command, and then only the files that match the task.
- `prompt` fetches the rules immediately before the work they apply to, so a
  long session does not lose them.
- The agent is told that the code wins. Where a note and the code disagree, it
  trusts the code and tells you.
- `update` asks first whether anything is worth writing down. Most sessions add
  nothing.

In a test on a real project, a knowledge base of 671 lines made the agent do
worse than no notes at all. Cut to 143 lines, it halved the time (95 seconds
against 202), lowered the cost ($0.49 against $0.56), and the agent changed the
right files.

So keep it small. Ask of every note: if it were deleted, would the agent make a
mistake that it does not make now? If the answer is no, delete it.

```{toctree}
:hidden:

Setup <setup>
Commands <commands>
Layout <layout>
OKF <okf>
Sharing <background-folders>
```
