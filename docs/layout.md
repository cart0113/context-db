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
│   └── ON_PROMPT.md ...         rules the agent sees on each command
├── acme-payments-project/       the project folder
│   ├── acme-payments-project.md describes the folder
│   ├── architecture.md
│   ├── data-model/
│   │   ├── data-model.md
│   │   └── entities.md
│   └── wip/                     optional
│       ├── wip.md               the list of work in progress
│       └── refund-endpoint.md
└── coding-standards/            a background folder
```

## The project folder

`<name>-project/` holds what is specific to this repository. It is the only
folder the commands write to.

What belongs in it:

- Conventions that the code does not show.
- Decisions, and the reasons for them.
- Mistakes that are easy to make here.
- Knowledge about the domain.

What does not belong in it is anything the agent can read from the code or its
comments: file layouts, function signatures, flags, summaries of modules, what a
function does. The knowledge base is not a mirror of the code. A note that
copies the code goes out of date as the code changes, and the agent trusts it
over the code. A fact about one piece of code belongs in a comment next to it.
Every command repeats this rule to the agent;
[Commands](commands.md#the-rule-every-command-repeats) shows the text.

## Background folders

Every other folder in `context-db/` is a background folder. It holds knowledge
that is not about this project in particular, such as coding standards, and it
usually lives in another repository. The commands read background folders and
never change them. [Sharing](#sharing) covers how to mount one.

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

The frontmatter is YAML, and YAML is fussy about a few characters. In a
description, avoid a colon followed by a space, and a space followed by `#`. If
you need them, put the whole description in double quotes. The checker tells you
when a description breaks these rules.

Keep a file to about 150 lines, and 200 at most. When a file outgrows that,
turn it into a folder.

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

Aim for 5 to 10 items in a folder. Beyond that its listing stops being a quick
read.

## Dynamic indexing

There are no `index.md` files. When the agent looks into a folder, it runs:

```bash
python3 .claude/skills/context-db/context-db.py toc context-db/acme-payments-project
```

The script reads the frontmatter of every file and subfolder in that folder and
prints one line for each, with its description:

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

The agent opens the files that match its task, and runs `toc` again on any
subfolder whose description does. Every command that reads the knowledge base
tells it to work this way.

A status of `draft` or `deprecated` is shown in brackets after the
description. A folder's own file appears only when it has more than frontmatter
in it; otherwise its description is shown one level up.

### Why there is no index.md

This is a design decision: it is how context-db implements OKF's `index.md`.

A generated file that is committed starts drifting from the files it describes
the moment someone edits a note and forgets to regenerate it. An agent that
reads a stale index misses notes that exist and looks for notes that are gone.
Keeping it in step needs a regenerate step after every write, a check in CI,
and a rule for merge conflicts, which is maintenance that adds nothing to the
knowledge itself.

A listing built on demand cannot drift. It is made from the files each time it
is asked for, so there is nothing to regenerate, commit, review, or merge, and
nothing for `update` or `maintain` to keep up to date.

It still does everything OKF's `index.md` is for:

- **Progressive disclosure.** The agent sees what a folder holds, one line per
  item, before it opens anything, and goes one level deeper only where a
  description matches.
- **Descriptions route the reader.** Each line carries the `description` from
  the file's frontmatter, so the description is still what makes a note
  findable.
- **The same layout.** The listing uses OKF's index layout: a `Subfolders` and a
  `Files` heading, then one `* [Title](path) - description` line per item.
- **Every folder, every bundle.** It works for the project folder, its
  subfolders, and every shared background folder, with nothing generated in the
  repository that owns it.

The one thing it gives up is browsing: on GitHub or in Obsidian you see the
files without their descriptions. [The OKF page](okf.md#dynamic-indexing) has
more on the choice.

## Links

Link between files with ordinary Markdown links, relative to the file you are
in:

```markdown
See the [retry policy](./retry-policy.md) and [the dispatcher](../../src/dispatch.py).
```

Do not start a link with `/`. GitHub reads that as the top of the repository,
and the link breaks.

## The wip folder

`wip/` inside the project folder is optional. It records the work in progress.
`wip/wip.md` is a short list with one line per piece of work: a link to its
plan, the date it started, the branch, and where it stands.

```markdown
- [Refund endpoint](refund-endpoint.md). Started 2026-11-03 on `feature/refunds`. Validation done; partial refunds undecided.
```

Each plan is a file next to `wip.md`, or a folder of files for a large piece of
work. Plans are deleted when the work lands. They can be as long as they need
to be.

```markdown
---
type: Plan
description: Adding POST /refunds through the ledger queue
status: draft
branch: feature/refunds
---
```

The [`wip` command](commands.md) keeps this folder up to date, and the checker
warns about a plan that `wip.md` does not list.

## Sharing

Some knowledge is not about one project. Coding standards, how your team uses
git, and notes on a library are examples. Keep knowledge like that in one place
and mount it into each project that needs it.

You mount it as a [background folder](#background-folders). `prompt` lists
background folders next to the project folder.

```text
context-db/
├── acme-payments-project/       this project's knowledge
├── coding-standards -> ...      shared, mounted with a symlink
└── git-standards -> ...         shared, mounted with a symlink
```

### Three rules

1. Mount a background folder at the top level of `context-db/`, and nowhere
   deeper.
2. Links inside a shared folder must stay inside it. A link that leaves the
   folder points at something that may not exist in the next project.
3. Notes in a shared folder are changed in the repository that owns it. The
   commands only read it here.

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

## What the checker looks for

`toc --check` reports these as errors:

- a file with no frontmatter, no `type`, or no `description`
- a `type` or `description` that is not valid YAML as written
- a `status` other than `draft`, `stable`, or `deprecated`
- a link to a file that does not exist, or a link that starts with `/`
- a folder with no file named after it
- a symlink inside the project folder or a background folder
- an `index.md` file, which context-db does not use

It reports these as warnings: a file over 200 lines outside `wip/`, and a
folder with more than 12 items.

Folders that contain no Markdown, such as a folder of images, are not part of
the knowledge base, and are neither listed nor checked. Because nothing is
committed, private notes that git ignores are listed for you and for no one
else.
