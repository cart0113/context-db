# The Open Knowledge Format

The files in a context-db knowledge base follow the Open Knowledge Format, or
OKF. This page explains what OKF is, where it came from, and how context-db
uses it.

## What OKF is

OKF is an open specification for writing knowledge down as Markdown files, so
that both people and AI agents can read it. It is published by Google Cloud
under the Apache 2.0 license and is not tied to any one agent or model.

The format is small. A folder of Markdown files is a *bundle*. Each file starts
with a few lines of metadata and continues as ordinary Markdown. Files link to
each other, and each folder can carry an `index.md` that lists what is in it.

Read the specification itself:
[OKF v0.2 specification](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md).
Section numbers on this page refer to it.

## A short history

April 2026
: Andrej Karpathy publishes a note called
  [LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).
  Most tools that give documents to an LLM search the raw documents again for
  every question. Karpathy suggests having the LLM keep a wiki instead: a set of
  linked Markdown pages that it updates as it learns, so that knowledge builds
  up over time.

June 2026
: Google Cloud announces
  [OKF version 0.1](https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing).
  The announcement credits Karpathy's note and describes OKF as a specification
  that "formalizes the LLM-wiki pattern into a portable, interoperable format".

July 2026
: [Version 0.2](https://cloud.google.com/blog/products/data-analytics/okf-v0-2-adds-trust-signals)
  adds optional fields for recording where a piece of knowledge came from, who
  has checked it, and when it goes out of date.

August 2026
: The specification moves into
  [its own repository](https://github.com/GoogleCloudPlatform/open-knowledge-format),
  along with sample bundles and a reference implementation.

November 2026
: One of the Google engineers behind OKF opens
  [a pull request](https://github.com/GoogleCloudPlatform/open-knowledge-format/pull/63)
  saying that development is moving to a vendor-neutral GitHub organization,
  `open-knowledge-format`, where version 0.3 is in progress. That repository was
  not yet public when this page was written.

## OKF in two minutes

- A **bundle** is a folder of Markdown files. It is the unit that gets shared.
- Each file is a **concept**: one piece of knowledge. It starts with a block of
  YAML called frontmatter and continues as ordinary Markdown.
- The frontmatter must have a `type`. Everything else is optional. OKF
  recommends `title`, `description`, `tags`, and `resource`.
- A folder can have an `index.md` that lists its contents with a one-line
  description each. A reader can see what is there before opening anything.
- A folder can have a `log.md` that records changes by date.
- Concepts link to each other with ordinary Markdown links.
- Optional fields record where a concept came from, who has checked it, and
  whether it is still current.

A bundle conforms to OKF when three things are true (section 11):

1. Every Markdown file other than `index.md` and `log.md` has frontmatter that
   parses as YAML.
2. That frontmatter has a `type` that is not empty.
3. Any `index.md` or `log.md` follows the layout the spec gives for it.

## How context-db uses OKF

Each top-level folder in `context-db/` is an OKF bundle. This is a file in one:

```markdown
---
type: Decision
description:
  Why refunds are processed asynchronously, and the idempotency-key rule that
  follows from it
---

# Asynchronous refunds
```

These are the parts of the specification that context-db uses:

| OKF | Section | How context-db uses it |
| --- | --- | --- |
| Bundles | 3 | Each top-level folder in `context-db/` is a bundle: the project folder, and every background folder. |
| Concepts | 4 | Every Markdown file in those folders is a concept. |
| `type` | 4.1 | Required, as in OKF. context-db suggests nine values and accepts any. |
| `description` | 4.1 | OKF recommends it. context-db requires it, because it is what the agent reads to decide whether to open a file. |
| `status` | 5.4 | Used as defined: `draft`, `stable`, or `deprecated`. |
| Links | 6.1 | Ordinary Markdown links, always in the relative form. |
| `index.md` | 8 | Built on demand by `toc`, in the list layout OKF gives, and never written to disk. See [Dynamic indexing](#dynamic-indexing). |
| `okf_version` | 12 | context-db implements OKF 0.2; `--version` and `toc --check` say so. With no root `index.md`, nothing in the folder records it. |
| Conformance | 11 | `toc --check` tests the three rules above, and a few stricter ones. |

The suggested values for `type` are `Decision`, `Convention`, `Rule`,
`Architecture`, `Gotcha`, `Reference`, `Research`, `Plan`, and `Folder`. OKF keeps no
registry of types, so these are context-db's own choice.

## The parts context-db leaves out

You can still use any of these in your own files. The checker ignores keys it
does not know about.

`title` (section 4.1)
: The page heading already gives the title. The listing uses the heading.

`tags` and `resource` (section 4.1)
: Tags only help when everyone uses the same words. Descriptions and folders
  already do that job. `resource` points at an outside asset such as a database
  table, and most project notes have none.

`log.md` (section 9)
: Git history already records what changed and when.

`sources`, `generated`, `verified`, and `stale_after` (section 5)
: These record where a concept came from, who checked it, and when it expires.
  For files in a git repository, `git log` and `git blame` already answer the
  first two. A "verified" field that nobody keeps up to date is worse than no
  field.

Attested computations (section 10)
: A way to prove that a number came from an approved query. It is meant for
  data catalogs and does not apply to project notes.

Links that start at the bundle root (section 6.1)
: OKF recommends links such as `/tables/orders.md`, which start from the top of
  the bundle. GitHub and most Markdown tools read a leading `/` as the top of
  the repository, so these links break whenever a bundle is a subfolder.
  context-db uses relative links, which OKF also allows.

## What context-db adds

OKF is a file format and nothing else. It does not say when an agent should
read the files, or what is worth writing down. That is what the
[five commands](commands.md) are for.

context-db also adds a few conventions. All of them are valid OKF.

A descriptor file for each folder
: OKF has no field for describing a folder. Its reference implementation asks an
  LLM to summarize what is inside. context-db uses a file named after the
  folder, such as `data-model/data-model.md`, and that file's description is the
  folder's description. To OKF it is one more concept.

A `wip/` folder
: Plans for the work in progress live in `wip/` inside the project folder and
  are deleted when the work lands. A plan can carry a `branch` key. OKF allows
  extra keys.

One project folder, any number of background folders
: The commands write to the project folder only. Other bundles are mounted
  beside it and are read-only. See [Sharing](layout.md#sharing).

Settings and rules kept outside the bundles
: The settings file and the `ON_*.md` files sit next to the bundles, not inside
  them, so every Markdown file inside a bundle is a real concept.

Stricter checks
: Besides the three OKF rules, `toc --check` fails on a missing description,
  a broken link, a folder with no descriptor, or a symlink inside a bundle. It
  also catches the common ways a description stops being valid YAML, such as a
  colon followed by a space.

## Dynamic indexing

OKF lets every folder carry an `index.md`: a list of what is in the folder, one
line per item with its description, so a reader can see what is there before
opening anything. The spec does not require the file. It says only that an
`index.md`, if there is one, follows its layout.

context-db implements the index dynamically. It never writes an `index.md`.
Whenever the agent looks into a folder, it runs the skill's `toc` command,
which reads the frontmatter of the files in that folder and prints the same
list, in OKF's layout, at that moment. The agent reads it, opens what it needs,
and runs `toc` again on a subfolder when it wants to go deeper.

The reason is that a generated file that is committed goes out of date. It
has to be rebuilt after every change, checked in CI, and regenerated after
every merge conflict, and an agent that reads a stale one misses notes or looks
for notes that are gone. A listing built on demand from the files cannot drift.
It also lets a folder shared from another repository work without that
repository generating anything, and it lets each user see their own private,
gitignored notes.

The cost is small. Someone browsing the folders on GitHub or in Obsidian sees
the files without their one-line descriptions.

## Where context-db departs from the LLM wiki

Karpathy's wiki is meant to grow. Every source the LLM reads adds pages,
because the LLM cannot cheaply read those sources again.

A code repository is different. The source is the code and its comments, and
the agent can read them whenever it wants. A page that repeats them is a second
copy that goes out of date. So context-db takes the format and not the habit of writing
everything down. Most sessions add nothing.
[Motivation](index.md#motivation) explains the reasoning.

## Using other tools

Each folder is a plain OKF bundle, so anything that reads Markdown with
frontmatter can read it: GitHub's file view, Obsidian, a static site generator,
or a tool built for OKF.

context-db's own tests parse the frontmatter of every file it ships with a
standard YAML library and check that `type` is present. That is the same check
OKF's reference parser makes.

## Keeping up with OKF

OKF is young and still changing. context-db relies mainly on the parts that have
not changed since version 0.1: frontmatter with a `type` and a `description`,
the `index.md` list layout, and Markdown links. The one newer piece it uses is
`status`, which arrived in version 0.2.
