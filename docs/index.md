---
html_theme.sidebar_secondary.remove: true
---

# context-db

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
```{button-ref} getting-started
:color: primary
:class: hero-button

Get started
```
```{button-ref} okf
:color: secondary
:outline:
:class: hero-button

About the Open Knowledge Format
```
::::

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

## A typical session

1. You type `/context-db prompt "add a refund endpoint"`.
2. The agent reads the index, opens the notes on the payments API and the plan
   for refunds, and skips everything else.
3. It writes the code.
4. You type `/context-db update --push`. The agent asks itself whether it
   learned anything that the next agent would get wrong without being told.
   Usually the answer is no, and it says so. If there is something, it writes a
   short note in the right place. Then it commits and pushes.

## Why use it

Agents lose track of a project's rules partway through a long session, and they
never knew the reasons behind your code in the first place. One large
instructions file does not fix this. Research has found that context files often
make agents perform worse: the agent follows the file and reads less of the
code.

A small knowledge base that the agent reads a little at a time, and only when
asked, does better. [Why it works this way](why.md) has the details and the
numbers.

```{toctree}
:hidden:

Get started <getting-started>
Commands <commands>
Knowledge base <knowledge-base>
OKF <okf>
Sharing <background-folders>
Why <why>
Migrating <migrating>
```
