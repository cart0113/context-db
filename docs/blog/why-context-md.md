# Why context-md?

*A look at how LLM context management has evolved, and why a dedicated standard helps.*

---

## The Skills Pattern

Anthropic's [SKILL.md standard](https://github.com/anthropics/skills) is a genuinely
good idea. The concept is simple: write a Markdown file with YAML front matter, put it
in a `skills/` directory, and an LLM assistant can discover and follow the procedure
described in that file. Name a skill well, give it a clear description, and the assistant
knows when to reach for it without being told.

The portability story is even better. A skill folder can be a symlink. A team that has
invested in a well-written code review procedure can publish it in a shared repository,
and every project that wants it just symlinks the folder. The procedure lives in one
place, gets maintained in one place, and every consumer benefits from improvements
automatically.

These are ideas worth copying.

## How Teams Actually Use Skills

Here is a pattern that appears again and again in real projects:

```
skills/
├── code_review.md          ← a procedure: how to review a pull request
├── git_workflow.md         ← a procedure: how to handle branches and commits
├── project_background.md   ← not a procedure: background on what the system does
├── architecture_notes.md   ← not a procedure: how the codebase is structured
└── coding_conventions.md   ← not a procedure: preferred patterns and style
```

The first two are genuine skills. The last three are not — they are reference material,
background knowledge, and context. But teams reach for the skills format anyway because:

1. It has a standard, recognized structure
2. It supports front matter with descriptions
3. It is portable via symlinks
4. It is already supported by the tools they are using

This is understandable. If the only tool you have is a hammer, everything looks like
a procedure. But mixing reference material into the skill namespace has real costs.

## The Problem with Context as Skills

**Skill subsystems are bounded.** Platforms that load skills have limits — in total
size, in how many can be loaded simultaneously, or in the cognitive overhead they
impose on the model. Filling those limits with reference material reduces capacity for
actual procedural skills.

**Procedures and knowledge are different things.** A skill says: *when X, do Y*. A
context document says: *this is what X is*. Putting both in the same namespace creates
confusion. Should the assistant *follow* the architecture notes, or just *use* them to
inform decisions?

**Discovery semantics differ.** Skills are invoked. Context is consulted. An LLM that
sees `architecture_notes.md` in a skills directory might try to follow it as a
procedure, or might correctly interpret it as background — but the format gives no
signal either way.

**Loading everything is expensive.** Skills are often loaded eagerly. Reference
material that should only be consulted when relevant gets loaded at the start of every
session, consuming tokens on every interaction even when irrelevant.

## What context-md Is

context-md takes the ideas worth keeping from the skills standard — front matter,
portability, standardized structure — and applies them specifically to the problem of
organizing background knowledge for LLMs.

The key insight is **progressive discovery**. Instead of loading everything upfront,
an LLM reads a lightweight index first — `CONTEXT_TOC.md` — that describes what
context is available. Based on the current task, it fetches only what it needs. A
question about the database schema doesn't need the UI component conventions loaded.
A refactoring task in the auth module doesn't need the billing architecture.

The index itself is auto-generated from the front matter of context documents and the
`CONTEXT.yml` configs of subfolders. Humans write context, add front matter, and run
one script. The discovery structure maintains itself.

## The Three Files

Every context node has three files with distinct roles:

**`CONTEXT.yml`** is configuration. It declares what this node is (title, description),
and controls what the script indexes (depth, ignore lists, read-only markers for
external resources). It is the only file that the script reads for metadata about the
node itself.

**`CONTEXT_INSTRUCTIONS.md`** is prose addressed directly to the LLM. Write here
whatever guidance is specific to this context node: which subfolder to load for API
work, key relationships to keep in mind, things that are easy to get wrong. This file
is human-written and never modified by the script.

**`CONTEXT_TOC.md`** is generated. Never edit it. It combines the title and
description from `CONTEXT.yml`, the prose from `CONTEXT_INSTRUCTIONS.md`, and
auto-generated tables of available subfolders and files. This is the only file the
LLM needs to read to understand what context exists and where to find it.

## Portability Is Preserved

One of the most valuable properties of the skills format carries over directly. Any
`CONTEXT/` subfolder can be a symlink to a shared resource. A team maintaining
shared coding conventions publishes them in one repository:

```
shared-context/
└── CODING_STYLE/
    ├── CONTEXT.yml
    ├── CONTEXT_TOC.md
    └── defensive_coding.md
```

Any project that wants these conventions symlinks the folder:

```bash
ln -s /path/to/shared-context/CODING_STYLE  your_project/CONTEXT/CODING_STYLE
```

The parent `CONTEXT/CONTEXT.yml` marks it as `read_only` so the build script doesn't
try to modify files in the shared repository. The conventions show up in the project's
TOC automatically, sourced from their canonical location.

## Why Not Just a Wiki?

Project wikis, Notion pages, and Confluence docs are great for human readers. They are
poor for LLMs because they have no standard structure, no machine-readable metadata,
no concept of progressive discovery, and no portability. They also tend to go stale
because updating them is a separate workflow from writing code.

context-md documents live in the repository, next to the code they describe. They are
version-controlled, reviewed, and updated as part of the normal development workflow.
The auto-generated TOC means they stay organized without extra effort.

## Relationship to SKILL.md

context-md is not a replacement for SKILL.md. It is a complement. The two systems
solve different problems and should coexist:

- **SKILL.md** — *what to do*: procedures, workflows, step-by-step instructions
- **context-md** — *what to know*: background, architecture, conventions, domain knowledge

Keep your skills lean and procedural. Keep your context organized and discoverable.
Both work better when they stay in their lane.

---

*context-md is open source. Contributions and feedback welcome at
[github.com/cart0113/context-md](https://github.com/cart0113/context-md).*
