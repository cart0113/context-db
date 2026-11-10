# The knowledge base

The knowledge base is the `context-db/` folder at the top of your repository.
This page describes what goes where and what a file looks like.

The file format is the [Open Knowledge Format](okf.md).

## Layout

```text
context-db/
├── context-db.json              shared settings
├── context-db.local.json        your own settings, gitignored (optional)
├── context-db-on-markdown/      rules the agent sees on every command
├── acme-payments-project/       the project folder
│   ├── acme-payments-project.md describes the folder
│   ├── index.md                 generated
│   ├── architecture.md
│   ├── data-model/
│   │   ├── data-model.md
│   │   ├── index.md
│   │   └── entities.md
│   └── wip/
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

What does not belong in it is anything the agent can read from the code: file
layouts, function signatures, summaries of modules. Notes like that go out of
date, and the agent trusts them over the code.

## Background folders

Every other folder in `context-db/` is a background folder. It holds knowledge
that is not about this project in particular, such as coding standards, and it
usually lives in another repository. The commands read background folders and
never change them. See [](background-folders.md).

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
description says what the folder holds, and that description is what appears in
the index one level up. The file needs nothing but frontmatter:

```markdown
---
type: Folder
description: Database schema — the payment, refund, and merchant entities
---
```

Aim for 5 to 10 items in a folder. Beyond that the index stops being a quick
read.

## index.md

Every folder has an `index.md` that lists what is in it:

```markdown
# Subfolders

* [data-model](data-model/index.md) - Database schema — the payment, refund, and merchant entities
* [wip](wip/index.md) - Plans for what is being built right now

# Files

* [API Reference](api-reference.md) - The REST API — authentication and the payments and refunds endpoints
* [Architecture](architecture.md) - The three services, what each one owns, and how they talk
* [PCI handling](pci-handling.md) - What may never be stored or logged, and what needs a security review
```

You never write these. `update` and `wip` regenerate them from the frontmatter.
A status of `draft` or `deprecated` is shown in brackets after the description.

## Links

Link between files with ordinary Markdown links, relative to the file you are
in:

```markdown
See the [retry policy](./retry-policy.md) and [the dispatcher](../../src/dispatch.py).
```

Do not start a link with `/`. GitHub reads that as the top of the repository,
and the link breaks.

## The wip folder

`wip/` inside the project folder holds plans for work in progress, one file per
piece of work. Plans are deleted when the work lands. They can be as long as
they need to be.

```markdown
---
type: Plan
description: Adding POST /refunds through the ledger queue
status: draft
branch: feature/refunds
---
```

The [`wip` command](commands.md) keeps this folder up to date.

## What the checker looks for

`index --check` reports these as errors:

- a file with no frontmatter, no `type`, or no `description`
- a `type` or `description` that is not valid YAML as written
- a `status` other than `draft`, `stable`, or `deprecated`
- a link to a file that does not exist, or a link that starts with `/`
- a folder with no file named after it
- a symlink inside the project folder or a background folder

It reports these as warnings: a file over 200 lines outside `wip/`, and a
folder with more than 12 items.

Two things are skipped. Folders that contain no Markdown, such as a folder of
images, are not part of the knowledge base. Anything that git ignores is left
out of the index and the checks, so you can keep private notes beside the
shared ones.
