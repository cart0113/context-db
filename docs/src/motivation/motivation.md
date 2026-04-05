# Motivation

## The goal: keep the loaded context small

AI coding tools give agents background knowledge through a single entry-point
file — `CLAUDE.md`, `AGENTS.md`, `.cursorrules`. For a small project, this works
fine. For a large one, it falls apart pretty quickly.

The limits are real. Anthropic recommends keeping `CLAUDE.md` under 200 lines.
Codex caps combined `AGENTS.md` at 32 KiB. Cursor recommends `.cursorrules`
under 500 lines. But the background knowledge needed to work in a large system —
architecture, data models, API contracts, deployment constraints, historical
decisions — doesn't fit in a few hundred lines. It just doesn't.

And loading everything eagerly isn't the answer either. Chroma Research tested
18 LLMs and found that performance degrades as input length increases — models
do best when relevant information appears at the beginning or end of context,
with "substantial performance gaps" as context grows. More context doesn't mean
better results; it means more noise.

So a single context file works until it doesn't. Past a few hundred lines,
agents start missing instructions. Breaking it into smaller documents solves the
length problem but creates a discovery problem — the agent doesn't know what
exists. A manually maintained table of contents drifts every time a document is
added or reorganized. And delegating index maintenance to the agent introduces
its own failure modes. The index needs to be generated from the documents
themselves.

## A familiar pattern: structured knowledge vaults

The idea of organizing knowledge in a hierarchy of interlinked documents isn't
new. Tools like Obsidian and Notion structure information as collections of
Markdown (or rich-text) files in nested folders, with metadata and linking to
make large knowledge bases navigable.

These tools solve the discovery problem for humans — browse a folder tree, read
a document, follow links to related material. The hierarchy provides a map; the
documents provide depth.

context-db applies this same structural pattern — folder hierarchy,
self-describing files, metadata-driven indexes — but targets LLM agents as the
reader instead of humans. Where a human navigates visually through a sidebar or
graph view, an agent reads a generated TOC of descriptions and paths, then
fetches only what it needs.

## Skills and their limits

Some teams organize background knowledge as skills. This can work, but honestly,
trying to structure _all_ the knowledge and context about a project into
discrete skills feels strange to me. Skills are fundamentally designed around
invocation — `/deploy`, `/review-pr`, `/run-tests` — not around representing the
kind of interconnected, layered knowledge that builds up in a real codebase.

There's also a free-form problem. Skills impose a rigid structure: each one
lives in its own directory with a `SKILL.md`, YAML frontmatter with strict
naming rules, specific discovery mechanisms. That's great when you're defining
an action or a bounded reference. But project knowledge isn't that neat. It's
architecture decisions that link to data model docs that reference deployment
constraints. Trying to carve all of that into standalone skill-sized units means
you're fighting the format instead of just writing things down.

That said, skills do have useful properties worth borrowing. YAML frontmatter
makes files self-describing. Vendors have built progressive disclosure on top.
And skills are portable — symlink a published folder and it works.

The progressive disclosure mechanism, however, is vendor-managed: each tool
decides when and how to surface skill content. Claude Code, Codex, and Cursor
each handle it differently. You write the files; the vendor controls discovery.
