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

The agent lists the knowledge base, opens the notes on the database schema and the plan
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
Code. They come as one folder and show up as five commands under `/context-db`.

The commands work on a folder in your repository called `context-db/`. That
folder is the knowledge base. It holds what an agent cannot work out by reading
your code and its comments: your conventions, the decisions you made and why,
the mistakes to avoid, and the plan for the work in progress. It is never a copy
of the code. What the code already says stays in the code.

Everything in it is a Markdown file with a short description at the top. When
the agent looks into a folder, the script lists what is inside, one line each
with its description, built from the files on the spot. The agent reads that
list, opens the one or two files it needs, and leaves the rest alone. Nothing is
generated ahead of time, so the list is never out of date.

There is no database and no server, in spite of the name. It is a folder of text
files and one Python script.

## The commands

::::{grid} 1 1 1 1
:gutter: 3

:::{grid-item-card} /context-db prompt
:class-card: command-card command-prompt
:link: commands
:link-type: doc

Before a task. Looks up what the knowledge base says about it.
:::

:::{grid-item-card} /context-db update
:class-card: command-card command-update
:link: commands
:link-type: doc

After a task. Writes down what the next agent would need, if anything. `--push`
also commits and pushes.
:::

:::{grid-item-card} /context-db wip
:class-card: command-card command-wip
:link: commands
:link-type: doc

Optional, for long work. Keeps a short list of the work in progress. `--list`,
`--cleanup`, `--clear`.
:::

:::{grid-item-card} /context-db configure
:class-card: command-card command-configure
:link: commands
:link-type: doc

First, and whenever you like. Sets context-db up by asking a few questions; edit
the files by hand afterwards.
:::

:::{grid-item-card} /context-db maintain
:class-card: command-card command-maintain
:link: commands
:link-type: doc

Now and then. Removes what the code and its comments already say, fixes what
has drifted, and splits and reorganizes. `--use-git-diff` also reads the git
history for what has gone out of date.
:::
::::

`/context-db --help` prints the same list.

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

:::{tab-item} A folder listing
The agent runs `context-db.py toc <folder>` and gets this, built from the files
as they are now:

```markdown
# Contents of `context-db/acme-payments-project/`

# Subfolders

* [data-model](context-db/acme-payments-project/data-model/) - Database schema — the payment, refund, and merchant entities
* [wip](context-db/acme-payments-project/wip/) - Work in progress, if the project records it

# Files

* [API Reference](context-db/acme-payments-project/api-reference.md) - The REST API — authentication and the payments and refunds endpoints
* [Architecture](context-db/acme-payments-project/architecture.md) - The three services, what each one owns, and how they talk
* [PCI handling](context-db/acme-payments-project/pci-handling.md) - What may never be stored or logged, and what needs a security review
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

The idea builds on Andrej Karpathy's
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

context-db keeps one rule above all, and repeats it to the agent on every
command: the knowledge base is not a mirror of the code. Anything an agent can
learn by reading the code and its comments stays there. A note that copies it is
a second version, and it drifts out of date every time the code changes, while
the next agent goes on trusting it. So the knowledge base keeps only what the
code cannot say: why a decision was made, the conventions and pitfalls the code
does not show, rules that come from outside, and the plan for the work in
progress. `update` follows that rule when it writes. `maintain` goes looking for
notes that break it.

context-db hands the agent small pieces of text at set points in the work
instead of one big file:

- `prompt`, right before a task: how to list the knowledge base, the plans for
  the work in progress, and your rules. The agent opens only the notes that
  match the task.
- `update`, after a task: what belongs in the knowledge base and what does not,
  so that it stays small.
- `maintain`, now and then: how to find notes that repeat the code or have
  drifted from it, and remove them.
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
