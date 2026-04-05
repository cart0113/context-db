# Motivation

## The problem: knowledge doesn't fit

AI coding tools give agents background knowledge through a single entry-point
file — `CLAUDE.md`, `AGENTS.md`, `.cursorrules`. This works for small projects.
It breaks down for large ones.

The limits are real: Anthropic recommends keeping `CLAUDE.md` under 200 lines.
Codex caps combined `AGENTS.md` at 32 KiB. Cursor recommends `.cursorrules`
under 500 lines. Meanwhile, the background knowledge needed to work in large
systems — architecture, data models, API contracts, deployment constraints,
historical decisions — doesn't fit in a few hundred lines.

Research confirms the gap. A 2025 arXiv study on a 108K LOC C# project found
that effective AI-assisted development required ~26,000 lines of structured
context — a 24% knowledge-to-code ratio. Single-file manifests at ~1,000 lines
were "an order of magnitude" insufficient.

Loading everything eagerly isn't the answer. Chroma Research tested 18 LLMs and
found that performance degrades as input length increases — models perform best
when relevant information appears at the beginning or end of context, with
"substantial performance gaps" as context grows. More context doesn't mean
better results; it means more noise.

## A familiar pattern: structured knowledge vaults

The idea of organizing knowledge in a hierarchy of interlinked documents isn't
new. Tools like Obsidian and Notion structure information as collections of
Markdown (or rich-text) files in nested folders, with metadata and linking to
make large knowledge bases navigable.

These tools solve the discovery problem for humans: browse a folder tree, read a
document, follow links to related material. The hierarchy provides a map; the
documents provide depth.

context-db applies this same structural pattern — folder hierarchy,
self-describing files, metadata-driven indexes — but targets LLM agents as the
reader instead of humans. Where a human navigates visually through a sidebar or
graph view, an agent reads a generated TOC of descriptions and paths, then
fetches only what it needs.

## The journey here

This project started with a single `CONTEXT.md` file explaining how a large
legacy system works. Architecture, data models, service boundaries, domain
quirks — everything an agent needs to reason about changes.

As the project grew, the file grew. Past a few hundred lines, agents started
missing instructions. The fix was obvious: break it into smaller documents. But
that created a discovery problem — how does the agent find what exists?

First attempt: manually maintain a table of contents in the root file. This
drifts every time you add or reorganize a document. Second attempt: a skill
(`/reindex`) to regenerate the TOC by reading individual files. This worked, but
required the agent to maintain the index correctly.

## Skills and their limits

Some teams organize background knowledge as skills. Skills have useful
properties: YAML frontmatter makes files self-describing, vendors have built
progressive disclosure on top (metadata at startup, full content on demand), and
skills are portable — symlink a published folder and it works.

But skills are designed around invocation — `/deploy`, `/review-pr`,
`/run-tests`. The progressive disclosure mechanism is vendor-managed: each tool
decides when and how to surface skill content. Claude Code, Codex, and Cursor
each handle it differently. You write the files; the vendor controls discovery.

## What context-db does

context-db takes the portable parts of skills — frontmatter, symlinks, standard
structure — and applies them to background knowledge, with one key difference:
**you control the discovery mechanism**.

A shell script generates `-toc.md` indexes from YAML frontmatter. Each TOC is a
list of descriptions with paths. An agent reads a TOC, decides what's relevant,
and fetches only those documents. Nested folders produce nested TOCs, supporting
arbitrarily deep hierarchies.

```
context-db-toc.md
├── acme-payments/acme-payments-toc.md
│   ├── architecture.md
│   ├── api-reference.md
│   └── data-model/data-model-toc.md
│       ├── entities.md
│       └── schema-conventions.md
└── coding-standards/coding-standards-toc.md
    ├── error-handling.md
    └── naming-conventions.md
```

The target is large projects with substantial background knowledge: legacy
systems, enterprise services, multi-team codebases. These are the projects where
a few hundred lines of context isn't enough, and an agent needs a map before it
can search.

## Discovery vs. retrieval

Claude Code has grep and glob. Cursor has RAG. Can't the agent just search?

These are **retrieval** mechanisms — they answer "find something matching this
query." A TOC is a **discovery** mechanism — it answers "here's what exists."

Without a map, the agent must already know what to search for. A grep for
"schema" finds schema-related files, but won't surface the deployment
constraints or API contracts that also matter. A TOC at startup gives the agent
a picture of available knowledge in a few hundred tokens, then lets it pull in
what it needs.

For small projects, built-in search is sufficient. The TOC becomes useful as
projects grow, as knowledge spans multiple domains, and especially when context
is shared across projects via symlinks — where the agent has no prior knowledge
of what's been linked in.

## Portability

Someone publishes a set of knowledge documents — coding standards, onboarding
guides, architecture overviews. Another project symlinks them:

```bash
ln -s /path/to/shared/coding-standards context-db/coding-standards
```

`build_toc.sh` reads the descriptions and generates a unified TOC, giving the
agent a map into an arbitrary collection of documents regardless of where they
live on disk. The build script never writes into symlinked folders.

Self-describing folders that compose into larger hierarchies without
coordination — this is the core portability mechanism.
