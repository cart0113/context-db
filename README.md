# context-db

A set of skills for coding agents. context-db helps you manage the project
knowledge needed for development and maintenance, kept as short Markdown notes
in your repo. It also provides a framework for managing usage information: the
knowledge others consume to navigate and use your project.

**Built on the [Open Knowledge Format](https://github.com/GoogleCloudPlatform/open-knowledge-format)
(OKF)**, an open standard for knowledge that agents can read.
[What OKF is, where it came from, and how context-db uses it](https://cart0113.github.io/context-db/okf.html).

Documentation: <https://cart0113.github.io/context-db/>

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

The agent lists the knowledge base, opens the notes on the database schema and
the plan for the receipts work, and skips everything else. Then it finds the
cause and proposes a fix.

When the work is done:

```text
/context-db update
```

The agent writes down anything the next agent would need. Most of the time
there is nothing to write down, and it says so.

To steer it, say what you want on the lines after the command:

```text
/context-db update

We talked a lot about how to use our custom grep tooling. Be sure to store
this knowledge so the next agent can pick up where we left off.
```

## Two kinds of knowledge

Project knowledge is internal: the decisions and their reasons, the
conventions, the pitfalls, the plans. It drives the work from day to day, and
nobody outside the project needs it.

Usage knowledge is external, and optional. It is the docs and API of your
project, expressed in OKF format and designed to be consumed by other
projects. Nobody needs context-db to read it, since it is plain OKF Markdown.

A project that does use context-db mounts your
[usage folder](https://cart0113.github.io/context-db/layout.html#usage-folders),
and its agent reads those notes the same way it reads its own. Its own
knowledge still comes first. It looks into yours when a task involves your
project, before it reads your code.

## Benefits

- Your project's knowledge is kept as a hierarchical wiki of short Markdown
  notes in your repo, in the [Open Knowledge Format](https://cart0113.github.io/context-db/okf.html). Every note has a
  one-line description, so the agent finds the few that match the task without
  reading a large instructions file on every turn.
- Two commands bracket the work: `/context-db prompt` before a task and
  `/context-db update` after it. The agent reads and writes the knowledge base
  when you say so, which refreshes its context during long work sessions.
- context-db is nothing more than context: canned instructions plus your own
  rules, sent when you run a command. Your rules are plain Markdown files in
  `context-db/configuration/`, named after the commands: `ON_PROMPT.md` is added
  to every `prompt` and `ON_UPDATE.md` to every `update`.
  [How it all fits together](https://cart0113.github.io/context-db/commands.html#how-it-all-fits-together) shows every word the agent receives.
- A small Python script builds each folder's OKF index
  [on the fly](https://cart0113.github.io/context-db/layout.html#dynamic-indexing), from the notes as they are at that moment. No `index.md`
  files are kept in your repo, so there is nothing to keep in sync and the
  index cannot drift from the notes.
- The knowledge base holds only what the code cannot say. Agents are told to
  watch for notes that repeat the code, because a copy drifts. `update` stores
  only what future agents need to know to be effective, and `maintain` clears
  out what has gone stale, so it stays small and efficient.
- `wip` keeps a short list of the work in progress with a plan for each, so a
  new session can pick up long work where the last one stopped: `prompt`
  starts from the plan, and `update` brings it up to date. It is useful on a
  new project, where one feature often takes many agent sessions.
- Shared standards and reference material are mounted as background folders.
  The agent is told which folders are background and which is the project's
  own, and it writes only to the project's. It knows which knowledge is
  critical to the project, and can still find background knowledge when it
  needs it.

## Install

Paste this into your coding agent, in the project where you want it:

```text
Set up context-db in this repository. Follow the Install steps in the README at
https://github.com/cart0113/context-db
```

The agent copies the skills into your project, asks you a few questions, and
creates the knowledge base. These are the steps it follows. You can also run
them yourself. You need Python 3.8 or newer.

1. Copy the skills into the project:

   ```bash
   git clone -b v0.1 https://github.com/cart0113/context-db /tmp/context-db
   mkdir -p .claude/skills
   cp -r /tmp/context-db/skill/context-db .claude/skills/
   ```

2. Set it up. An agent runs this command and follows the instructions it
   prints:

   ```bash
   python3 .claude/skills/context-db/context-db.py configure
   ```

   In Claude Code you can type `/context-db configure` instead. To set it up
   with no agent at all, run the same script with `configure --project <name>`.

[Setup](https://cart0113.github.io/context-db/setup.html) has the full steps.

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

```
your-project/
├── .claude/skills/context-db/      the skills: SKILL.md, context-db.py, prompts/
└── context-db/
    ├── configuration/              settings and rules, all plain Markdown
    │   ├── settings.md             project name, Python command, main branch
    │   ├── ON_PROMPT.md ...        the project's rules for each command
    │   └── ON_PROMPT.local.md ...  your own rules, gitignored (optional)
    ├── acme-payments-project/      the project folder: project knowledge
    │   ├── architecture.md
    │   ├── data-model/
    │   ├── acme-payments-usage/    a usage folder: usage knowledge (optional)
    │   └── wip/                    optional: wip.md lists the work in progress
    ├── coding-standards/           a background folder shared with other projects
    └── acme-ledger-usage -> ...    the usage folder of a project that yours uses
```

## The commands

The commands, as you type them:

```text
Before a task
  /context-db prompt <prompt: question or task>  navigate the OKF notes by what you ask
  /context-db prompt --audit <prompt>            the same, and show what it read and why

After a task, from what this session learned
  /context-db update                             write down what the next agent needs
  /context-db update <steering-guidance>         the same, steered by what you say

During long work
  /context-db wip                                write down where the work stands
  /context-db wip --list                         show what is in progress
  /context-db wip --maintain                     check every plan, delete what has landed
  /context-db wip --clear                        delete every plan

Rarely, as a spring cleaning, checked against git
  /context-db maintain                           cut what is stale, repeated, not needed
  /context-db maintain <folder or topic>         only there

First, and whenever you like
  /context-db configure                          set up, or change how the agent behaves

On any command
  --show-context                                 show the message it sends, and stop
  --help                                         its options
```

Each command is a starting point. It opens the conversation with the
instructions you would otherwise type yourself every time. That is all
context-db does: it saves you from saying the same things over and over.
`prompt`, `update`, and `maintain` cover the whole knowledge base, and no flag
narrows them. To narrow one, or to change how it works, say so in plain words
on the lines after it, as many as you like, or at any point later in the
conversation:

```text
/context-db update

Only the usage folder. The refund endpoint now needs an idempotency key.
```

`update` goes by what the agent remembers of the session. `maintain` compares
the knowledge base with the code and the git history. Either can be told
otherwise: ask `update` to read a `git diff` as well, or `maintain` to leave
git out. [A command is a starting point](https://cart0113.github.io/context-db/commands.html#a-command-is-a-starting-point) has more examples.

To see what the agent took from the knowledge base for a task, add `--audit`
to `prompt`. The agent reads as it always does, and then shows you what it
read and what led it there. Use that to design a better knowledge base.
[See what the agent read](https://cart0113.github.io/context-db/commands.html#see-what-the-agent-read) has an example.

- [`/context-db prompt`](https://cart0113.github.io/context-db/commands.html#context-db-prompt):
  Before a question or task. Navigates the Open Knowledge Format files of the
  knowledge base, based on what you ask.
- [`/context-db update`](https://cart0113.github.io/context-db/commands.html#context-db-update):
  After a task. Writes down what this session learned, if the next agent would
  need it.
- [`/context-db wip`](https://cart0113.github.io/context-db/commands.html#context-db-wip):
  Optional, for long work. Keeps a short list of the work in progress.
  `--list`, `--maintain`, `--clear`.
- [`/context-db maintain`](https://cart0113.github.io/context-db/commands.html#context-db-maintain):
  Rarely, as a spring cleaning. Goes through the whole knowledge base against
  the code and the git history: removes what the project already says and what
  is no longer needed, fixes what has drifted, and splits and reorganizes.
- [`/context-db configure`](https://cart0113.github.io/context-db/commands.html#context-db-configure):
  First, and whenever you like. Sets context-db up by asking a few questions;
  edit the files by hand afterwards.

`/context-db --help` prints the same list.

Nothing is loaded when a session starts. The agent reads the knowledge base when
you run one of these commands. After `/context-db prompt` it may also add to it
as it works; `/context-db configure` asks whether you want that.

You add your own rules to a command's instructions in a few plain Markdown
files in `context-db/configuration/`, and edit them by hand. `ON_PROMPT.md`
holds the project's rules for `prompt`, shared with everyone.
`ON_PROMPT.local.md` holds rules that are only yours, and is gitignored. The
other commands have the same pair. `/context-db configure` is a helper that
writes a first version of them by asking you a few questions.

Outside Claude Code, run the same commands from a terminal:

```bash
python3 .claude/skills/context-db/context-db.py prompt "add a refund endpoint"
```

## Motivation

An agent working on a large project needs context that the code does not give
it, and context-db provides a system for managing that context as it grows. It
is a hierarchy of short notes in your repository, and the agent reads only the
ones that match the task, when you ask it to.

That improves on one large `AGENTS.md` or `CLAUDE.md` file, which is linear
and is loaded in full into every session, so most of what the agent reads has
nothing to do with the task.

The idea builds on Andrej Karpathy's
[LLM wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f):
have the LLM keep a wiki of what it has learned, instead of working everything
out again each time.

`update` and `maintain` guide the agent to keep the knowledge base concise and
hierarchical, and never to duplicate what it can find by reading the code, the
docs, or the project's other assets. `update` writes down only what the next
agent would get wrong without it, and most sessions add nothing. `maintain`
goes back over everything: it cuts what has gone stale and what repeats the
code, and splits what has grown into shorter files and deeper folders, so
that the right note stays easy to find.
[The rule every command repeats](https://cart0113.github.io/context-db/commands.html#the-rule-every-command-repeats) has the exact text.

## Documentation

- [Setup](https://cart0113.github.io/context-db/setup.html)
- [Commands](https://cart0113.github.io/context-db/commands.html), with the
  exact text each one gives the agent
- [Layout](https://cart0113.github.io/context-db/layout.html): what goes where
  in the knowledge base, what a file looks like, and how to share knowledge
  between projects
- [The Open Knowledge Format](https://cart0113.github.io/context-db/okf.html):
  what it is and which parts context-db uses

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

MIT. See [LICENSE](LICENSE).
