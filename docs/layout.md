# Layout

The knowledge base is the `context-db/` folder at the top of your repository.
This page describes what goes where and what a file looks like.

The file format is the [Open Knowledge Format](okf.md).

## The whole folder

```text
context-db/
├── configuration/               settings and rules, all plain Markdown
│   ├── settings.md              shared settings
│   ├── settings.local.md        your own settings, gitignored (optional)
│   ├── ON_PROMPT.md ...         the project's rules for each command
│   └── ON_PROMPT.local.md ...   your own rules, gitignored (optional)
├── acme-payments-project/       the project folder
│   ├── acme-payments-project.md describes the folder
│   ├── architecture.md
│   ├── data-model/
│   │   ├── data-model.md
│   │   └── entities.md
│   ├── acme-payments-usage/     a usage folder, optional
│   │   ├── acme-payments-usage.md
│   │   └── calling.md
│   └── wip/                     optional
│       ├── wip.md               the list of work in progress
│       └── refund-endpoint.md
├── coding-standards/            a background folder
└── acme-ledger-usage -> ...     the usage folder of a project that yours uses
```

## Where each thing goes

Everything your project knows has one place to live, and only one. A second
copy goes out of date as soon as the first one changes, and nobody can tell
which of the two is wrong. So the knowledge base holds only what has no other
home.

| What | Where it lives | Who writes it |
| --- | --- | --- |
| What the code does | The code | You |
| A fact about one piece of code | A comment next to that code | You. The agent suggests the comment. |
| How to use your project, for people | Your README and your docs | You |
| Project knowledge: what an agent needs in order to work on your project, and cannot read from any of those | The [project folder](#the-project-folder) | `update` and `maintain` |
| Usage knowledge: what an agent in another project needs in order to use yours, and your docs do not say | A [usage folder](#usage-folders) | `update` and `maintain`, once you have one |
| Where the work in progress stands | The [`wip/` folder](#the-wip-folder) | `wip`, and `update` for the plan a session worked from |
| Rules the agent must see every time a command runs | The [ON files](commands.md#rule-files) | You, or `configure` |
| What another project knows, or your whole team | [Background folders](#background-folders) and [global context](#global-context) | Their owners. Your agent only reads them. |

The commands repeat this to the agent whenever it writes. When it learns
something that belongs in another row, it says so and writes no note.

## The project folder

`<name>-project/` holds project knowledge: what is specific to this repository,
for agents working on it. It is the knowledge the agent starts with on every
task.

What belongs in it:

- Conventions that the code does not show.
- Decisions, and the reasons for them.
- Mistakes that are easy to make here.
- Knowledge about the domain.

What does not belong in it is anything the agent can read from the project:
file layouts, function signatures, flags, summaries of modules, what a function
does, anything your docs already say. The knowledge base does not duplicate
them. A note that copies the code goes out of date as the code changes, and the
agent trusts it over the code. A fact about one piece of code belongs in a
comment next to it. Every command sends this rule to the agent;
[Commands](commands.md#the-no-duplication-rule) shows the text.

## Usage folders

A usage folder holds usage knowledge, for agents working in other projects
that use yours: your docs and API as those agents need them, expressed in OKF
format. An agent in a project that uses yours reads it the way it reads its
own notes, one line of description first and a file only when the task calls
for it. Nobody needs context-db to read it, since it is plain OKF Markdown.

It holds the bare minimum: where to start, which way in is right for which
job, the rules a caller must follow that the interface does not enforce, and
the mistakes callers make.

It is not a second copy of your docs. A usage note never reprints an API, a
schema, or a list of flags, because your README, your docs, and the definition
of your API already say those things, and a copy drifts. The note says where
they are and adds only what they leave out. Project knowledge stays out as
well: it belongs in the project folder.

This is a whole usage note, from the
[example](https://github.com/cart0113/context-db/tree/v0.1/example) that comes
with the repository:

```{literalinclude} ../example/acme-ledger-repo/okf/acme-ledger-usage/posting.md
:language: markdown
```

A usage folder is optional, and nothing creates one until you ask. Tell
`update` to start it:

```text
/context-db update

Start a usage folder. Other teams call the refunds API, and they keep
getting the idempotency key wrong.
```

By default it is a folder inside the project folder, named after the project:

```text
context-db/
└── acme-payments-project/
    ├── architecture.md              for agents working on acme-payments
    └── acme-payments-usage/         for agents in projects that use it
        ├── acme-payments-usage.md   describes the folder
        └── calling.md
```

Once the folder exists, the everyday commands look after it along with the
project folder. No flag is needed.

| Typed | What the agent does in a usage folder |
| --- | --- |
| `/context-db update` | Writes down what other projects need to know, if the session changed any of it. |
| `/context-db maintain` | Removes what your project already tells its users, moves project knowledge out, and fixes what has drifted. |

To work on the usage folder alone, say so: "Only the usage folder."

### Keeping it somewhere else

Some teams keep what other projects read apart from the knowledge base. The
`usage_folders` setting says where the folder is:

```yaml
---
project: acme-payments
python: python3
main_branch: main
usage_folders: okf/acme-payments-usage
---
```

The path is read from the top of your repository. `{project}` in it stands for
the project name, so `okf/{project}-usage` means the same as the line above. Use
that form in a [settings file that several projects share](setup.md#settings-from-other-files).

### More than one

A project whose users fall into separate groups can keep a usage folder for
each: one for the services that call its API, say, and one for the people who
run it. Name them as a list:

```yaml
usage_folders:
  - okf/acme-payments-usage
  - okf/acme-payments-admin-usage
```

Each folder stands on its own. It has a description of its own, a project that
uses yours mounts only the ones it needs, and a link never crosses from one to
another. `update` puts a note in the folder whose readers need it, and never
the same thing in two. It does not start a folder that the setting does
not name. Adding one is your decision.

### How another project reads it

A project that uses yours can [mount](#sharing) your usage folder in its own
`context-db/`, or find it where it is with [global context](#global-context).
Either way, every `/context-db prompt` in that project lists your usage folder
after its own folders, with its description. That description is the one line
another project's agent sees before it decides whether to look inside, so it
matters more than any other line in the folder.

This is what the agent of the example project sees. The first two folders are
its own. The last belongs to the ledger, a project that it uses:

```markdown
# Folders

- **Project folder** `context-db/acme-payments-project/`: Acme Payments — the payment service's architecture, API, data model, PCI handling rules, and the plans for work in progress
- **Usage folder** `context-db/acme-payments-project/acme-payments-usage/`: How to use Acme Payments from another service — where its API is described, and the rules every caller must follow that the API does not enforce (idempotency keys, asynchronous refunds, card tokens only)

# Global Context

- **Global folder** `../acme-ledger-repo/okf/acme-ledger-usage/`: How to use the Acme Ledger from another service — where its API is described, and the posting rules that the API does not enforce (entries that balance, amounts in minor units, never changing a posted entry)
```

That agent reads your usage folder the way it reads its own notes: the same
`toc` listing, the same kind of short file. It is told to look there before it
reads your code, whenever a task involves your project, and it never changes
anything in it.

Its own project knowledge still comes first, because that applies to
everything done in its repository. Your usage folder applies only where the
task involves your project.

Because the folder is read from wherever it is mounted, a file in it links only
to files inside the folder. To point at anything else, it gives a URL, or the
path from the top of your repository.

## Background folders

Every other folder in `context-db/` is a background folder. It holds knowledge
that is not about this project in particular, such as coding standards or the
usage folder of a project that yours uses, and it usually lives in another
repository. The commands read background folders and never change them.
[Sharing](#sharing) covers how to mount one.

## Global context

Some knowledge is better left where it is. A project that needs the
[usage folder](#usage-folders) of another can read it in place, with nothing
copied or linked. context-db calls this global context.

The `global_context` setting, in `context-db/configuration/settings.md`, says
where to look:

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

Each value is a glob pattern that matches the folders themselves, read from the
top of your repository wherever the command is run from. One pattern can go on
the setting's own line. The first one here matches every folder whose name
ends in `-usage` inside the `okf/` folder of your own repository. The second
matches the same in each repository next to yours. A pattern can also start
with `~` or `/`. For usage folders that are kept in the usual place, the
pattern is `../*/context-db/*-project/*-usage`.

`prompt` lists every folder that a pattern matches, after the project folder and
the background folders, one line each with its description:

```markdown
# Global Context

- **Global folder** `../acme-ledger/okf/ledger-usage/`: How to call the ledger service, and the idempotency rules
- **Global folder** `../acme-billing/okf/billing-usage/`: Invoice numbering and the rate tables
```

The agent looks into one only when its description matches the task, and it
never changes one. `update` and `maintain` do not list them.

The description comes from the file named after the folder, the same as for any
[folder](#a-folder): `ledger-usage/ledger-usage.md` here. A folder that
`context-db/` already holds, such as a mounted background folder, is not listed
a second time. Neither are your own usage folders, which `prompt` lists next to
the project folder.

The setting can also go in `settings.local.md`, when the way your machine is
laid out is not the way your teammates' machines are.

## Sharing

Some knowledge is not about one project: coding standards, how your team uses
git, the [usage folder](#usage-folders) of a project that yours uses. Keep it
in one place, and copy or symlink it into each project that needs it, as a
[background folder](#background-folders). `prompt` lists background folders
next to the project folder.

That suits a few folders that you choose one by one. To have the agent find
notes in whatever repositories are checked out next to yours, with nothing
copied or linked, use [global context](#global-context).

```text
context-db/
├── acme-payments-project/       this project's knowledge
├── coding-standards -> ...      shared, mounted with a symlink
├── git-standards -> ...         shared, mounted with a symlink
└── acme-ledger-usage -> ...     how to use the ledger, mounted from its repository
```

### Three rules

1. Mount a background folder at the top level of `context-db/`, and nowhere
   deeper.
2. Links inside a shared folder must stay inside it. A link that leaves the
   folder points at something that may not exist in the next project.
3. Notes in a shared folder are changed in the repository that owns it. The
   commands only read it here. When the agent learns something that belongs in
   another project's usage folder, it tells you what that folder should say.

### Ways to mount a folder

| Method | Who sees it | In git | How it updates |
| --- | --- | --- | --- |
| A copy | Everyone | Yes | You copy it again |
| A symlink that is gitignored | Only you | No | It follows the other repository |
| A git submodule and a symlink | Everyone | Yes, pinned | `git submodule update` |

### Mounting a folder only for you

```bash
cd context-db
ln -s ~/work/standards/context-db/coding-standards coding-standards
echo "context-db/coding-standards" >> ../.gitignore
```

Your agent sees the folder. Your teammates' agents do not, and nothing in git
changes. This works because the list of folders is built fresh every time
`prompt` runs.

The symlink can have a different name from the folder it points at.

### Mounting a folder for the whole team

```bash
git submodule add https://github.com/your-org/standards.git external/standards
cd context-db
ln -s ../external/standards/context-db/coding-standards coding-standards
```

Commit the submodule and the symlink.

### Shared folders need no preparation

A mounted folder is listed the same way as the project folder, on the spot, so
the repository that owns it does not have to generate anything first. To check
its format, run `toc --check` on it in either repository:

```bash
python3 <path-to>/context-db.py toc context-db/coding-standards --check
```

## A file

```markdown
---
type: Decision
description:
  Why refunds are processed asynchronously, and the idempotency-key rule that
  follows from it
---

# Asynchronous refunds

Refunds go through the ledger queue. Never process one inline.
```

The block between the `---` lines is the frontmatter.

| Key | Required | Meaning |
| --- | --- | --- |
| `type` | yes | The kind of knowledge. Use `Decision`, `Convention`, `Rule`, `Architecture`, `Gotcha`, `Reference`, `Research`, `Plan`, or `Folder`. Make up another only when none of these fits. |
| `description` | yes | One or two lines. This is all the agent sees before it decides whether to open the file, so be specific. |
| `status` | no | `draft` or `deprecated`. Leave it out when the content is current. |
| `branch` | no | The git branch a plan belongs to. Used only in `wip/`. |

A good description names what is in the file. "Scheduler execution flow and the
budget enforcement hook" works. "Architecture overview" does not. If a topic
goes by several names, put them all in.

A description that needs more than a line or two is a sign that the file holds
several topics. Split the file, one topic to a file, and each description gets
short again. The checker warns when a description passes 300 characters.

The frontmatter is YAML, and YAML is fussy about a few characters. In a
description, avoid a colon followed by a space, and a space followed by `#`. If
you need them, put the whole description in double quotes. The checker tells you
when a description breaks these rules.

Keep a file to one topic and about 150 lines, 200 at most. When a file outgrows
that, turn it into a folder.

## A folder

Every folder has a file named after it, such as `data-model/data-model.md`. Its
description says what the folder holds, and that description is what appears
when the folder one level up is listed. The file needs nothing but frontmatter:

```markdown
---
type: Folder
description: Database schema — the payment, refund, and merchant entities
---
```

Say what kind of thing is in the folder, and leave the list of its files to the
listing. Aim for 5 to 10 items in a folder. Beyond that its listing stops being
a quick read.

Short files in a tree of small folders are what let an agent find one note
without reading the others. It reads a few descriptions at each level, goes one
level down where a description matches, and opens one short file at the end.

## Dynamic indexing

By default context-db keeps no `index.md` files, in the project folder or in a
usage folder. When the agent looks into a folder, it runs:

```bash
python3 .claude/skills/context-db/context-db.py toc context-db/acme-payments-project
```

The script reads the frontmatter of every file and subfolder in that folder and
prints one line for each, with its description:

```markdown
# Contents of `context-db/acme-payments-project/`

# Subfolders

* [acme-payments-usage](context-db/acme-payments-project/acme-payments-usage/) - How to use Acme Payments from another service — where its API is described, and the rules every caller must follow
* [data-model](context-db/acme-payments-project/data-model/) - Database schema — the payment, refund, and merchant entities
* [wip](context-db/acme-payments-project/wip/) - Work in progress, if the project records it

# Files

* [API Reference](context-db/acme-payments-project/api-reference.md) - The REST API — authentication and the payments and refunds endpoints
* [Architecture](context-db/acme-payments-project/architecture.md) - The three services, what each one owns, and how they talk
* [PCI handling](context-db/acme-payments-project/pci-handling.md) - What may never be stored or logged, and what needs a security review
```

The agent opens the files that match its task, and runs `toc` again on any
subfolder whose description does. Every command that reads the knowledge base
tells it to work this way.

A status of `draft` or `deprecated` is shown in brackets after the
description. A folder's own file appears only when it has more than frontmatter
in it; otherwise its description is shown one level up.

### Why there is no index.md

This is how context-db implements OKF's `index.md`: it builds the listing on
demand and commits nothing.

A generated file that is committed starts drifting from the files it describes
the moment someone edits a note and forgets to regenerate it. An agent that
reads a stale index misses notes that exist and looks for notes that are gone.
Keeping it in step takes a regenerate step after every write, a check in CI,
and a rule for merge conflicts.

A listing built on demand cannot drift, and it still does what an `index.md`
is for. The agent sees what a folder holds, one line per item with its
description, before it opens anything, and goes a level deeper only where a
description matches. The listing uses OKF's own layout: a `Subfolders` and a
`Files` heading, then one `* [Title](path) - description` line per item. It
works for every folder, shared background folders included, with nothing
generated in the repository that owns them.

The one thing it gives up is browsing: on GitHub or in Obsidian you see the
files without their descriptions. [The OKF page](okf.md#dynamic-indexing) has
more on the choice.

### Keeping index.md files anyway

The standard OKF way is an `index.md` in each folder, and you may want that:
for people who browse the folders on GitHub or in Obsidian, or for an OKF tool
that reads your usage folder without context-db. Keep them, by hand or with a
commit hook that builds them. context-db works with both ways:

- The checker accepts an `index.md` in your project folder and in a usage
  folder.
- `toc` still lists those folders from their files. The agent is told to use
  `toc` and not to read an `index.md`, so it never reads an index that is out
  of date.
- When an `index.md` there stops matching its folder, the checker warns. It
  names the files and subfolders the index does not list, and the lines that
  point at something that is gone.
- When the agent adds, renames, or deletes a file in a folder that has an
  `index.md`, it is told to bring the index in step.

context-db does not build `index.md` files itself. A folder with an `index.md`
still needs the file named after it, because that file is where the folder's
description comes from.

### A folder that comes with an index

A folder written by another OKF tool often has an `index.md`, and context-db
uses it. When a background folder or a global folder has an `index.md`, `toc`
prints that file, with its links rewritten so that they work from where you
are. When it has none, `toc` builds the listing as usual. This is decided
folder by folder, so one folder can bring an index while its subfolders do not.

A folder like that often has no file named after it either. `prompt` then
describes it by the names its index lists.

## Links

Link between files with ordinary Markdown links, relative to the file you are
in:

```markdown
See the [retry policy](./retry-policy.md) and [the dispatcher](../../src/dispatch.py).
```

Do not start a link with `/`. GitHub reads that as the top of the repository,
and the link breaks.

A file in a [usage folder](#usage-folders) links only to files inside that
folder. Other projects read it from wherever they mount it, and a link that
leaves it leads nowhere there.

## The wip folder

`wip/` inside the project folder is optional. It records the work in progress.
`wip/wip.md` is a short list with one line per piece of work: a link to its
plan, the date it started, the branch, and where it stands.

```markdown
- [Refund endpoint](refund-endpoint.md). Started 2026-11-03 on `feature/refunds`. Validation done; partial refunds undecided.
```

Each plan is a file next to `wip.md`, or a folder of files for a large piece of
work. A plan is opened at the start of every session on that work, so it holds
what the next session needs in order to go on: the goal, the approach, what is
next, and what is undecided. What is done shrinks to a line, because the code
and the git log hold the rest. Plans are deleted when the work lands. They have
no size limit.

```markdown
---
type: Plan
description: Adding POST /refunds through the ledger queue
status: draft
branch: feature/refunds
---
```

[`wip`](commands.md#context-db-wip) writes the plans, `update` keeps the one a
session worked from up to date, `wip --maintain` and `maintain` check them
all, and the checker warns about a plan that `wip.md` does not list.

## What the checker looks for

`toc --check` reports these as errors:

- a file with no frontmatter, no `type`, or no `description`
- a `type` or `description` that is not valid YAML as written
- a `status` other than `draft`, `stable`, or `deprecated`
- a link to a file that does not exist, or a link that starts with `/`
- a folder with no file named after it, unless it is a folder from elsewhere
  that has an `index.md` of its own
- a symlink inside the project folder or a background folder
- a link in a usage folder that leaves it

It reports these as warnings:

- a file over 200 lines outside `wip/`
- a description over 300 characters
- a folder with more than 12 items
- an `index.md` in the project folder or a usage folder that does not match
  what its folder holds

The first three are the sizes that keep the knowledge base quick to search:
what the agent reads before it opens a file, what it loads when it does, and
what it scans at each level.

Folders that contain no Markdown, such as a folder of images, are not part of
the knowledge base, and are neither listed nor checked. Because nothing is
committed, private notes that git ignores are listed for you and for no one
else.
