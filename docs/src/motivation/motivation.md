# Motivation

## The goal: keeping the loaded context to a minimum

AI coding tools give agents background knowledge through a single entry-point
file — `CLAUDE.md`, `AGENTS.md`, `.cursorrules`. This works for small projects.
It breaks down for large ones.

The limits are real: Anthropic recommends keeping `CLAUDE.md` under 200 lines.
Codex caps combined `AGENTS.md` at 32 KiB. Cursor recommends `.cursorrules`
under 500 lines. Meanwhile, the background knowledge needed to work in large
systems — architecture, data models, API contracts, deployment constraints,
historical decisions — doesn't fit in a few hundred lines.

Loading everything eagerly isn't the answer. Chroma Research tested 18 LLMs and
found that performance degrades as input length increases — models perform best
when relevant information appears at the beginning or end of context, with
"substantial performance gaps" as context grows. More context doesn't mean
better results; it means more noise.

A single context file works until it doesn't. Past a few hundred lines, agents
start missing instructions. Breaking it into smaller documents solves the length
problem but creates a discovery problem — the agent doesn't know what exists. A
manually maintained table of contents drifts every time a document is added or
reorganized. Delegating index maintenance to the agent introduces its own
failure modes. The index needs to be generated from the documents themselves.

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

## Skills and their limits

Some teams organize background knowledge as skills. Fitting all project
knowledge into a skills format is a stretch — skills are designed around
invocation (`/deploy`, `/review-pr`, `/run-tests`), not background knowledge.

But skills have useful properties worth borrowing: YAML frontmatter makes files
self-describing, vendors have built progressive disclosure on top, and skills
are portable — symlink a published folder and it works.

The progressive disclosure mechanism, however, is vendor-managed: each tool
decides when and how to surface skill content. Claude Code, Codex, and Cursor
each handle it differently. You write the files; the vendor controls discovery.
