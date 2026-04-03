---
description: Why context-db exists and the problem it solves
---

# Motivation

## The problem: knowledge doesn't fit

AI coding tools give agents background knowledge through a single entry-point file — `CLAUDE.md`, `AGENTS.md`, `.cursorrules`. This works for small projects. It breaks down for large ones.

The limits are real: Anthropic recommends keeping `CLAUDE.md` under 200 lines. Codex caps combined `AGENTS.md` at 32 KiB. Cursor recommends `.cursorrules` under 500 lines. Meanwhile, a typical enterprise system is 5–20 million lines of code. A 20M LOC codebase is roughly 160–240 million tokens — two orders of magnitude larger than a 1M token context window. The background knowledge needed to work safely in these systems — architecture, data models, API contracts, deployment constraints, historical decisions — can't fit in a few hundred lines.

Research confirms the gap. A 2025 arXiv study on a 108K LOC C# project found that effective AI-assisted development required ~26,000 lines of structured context documentation — a 24% knowledge-to-code ratio. Single-file manifests at ~1,000 lines were "an order of magnitude" insufficient. The author organized context into three tiers: a small constitution always loaded, specialist agent instructions loaded per task, and a knowledge base retrieved on demand.

Loading everything eagerly isn't the answer either. Chroma Research tested 18 LLMs and found that performance degrades non-uniformly as input length increases — models perform best when relevant information is at the beginning or end of context, with "substantial performance gaps" as context grows from ~300 to ~113K tokens. More context doesn't mean better results; it means more noise.

## The journey here

This project started with a `CONTEXT.md` file — a harness-agnostic entry point (like `CLAUDE.md`) that explained how a large legacy system works. Architecture, data models, service boundaries, domain quirks — everything an agent needs to reason about code changes and bug fixes.

As the project grew, the file grew. Past a few hundred lines, agents started missing instructions. The fix was obvious: break it into smaller documents. But that created a new problem — how does the agent discover what exists?

First attempt: manually maintain a table of contents in the root file. This drifts every time you add or reorganize a document. Second attempt: a skill (`/reindex`) to regenerate the TOC by reading individual files. This worked, but required invoking the skill and depended on the agent to maintain the index correctly.

## What skills got right

Meanwhile, some teams were using skills to organize background knowledge. Skills have good properties for this: YAML front matter makes each file self-describing, vendors have built progressive disclosure on top (metadata at startup, full content on demand), and skills are portable — symlink a published folder and it works.

## Where skills fall short for knowledge

Skills are designed around invocation — `/deploy`, `/review-pr`, `/run-tests`. The progressive disclosure mechanism is vendor-managed: each tool decides when and how to surface skill content. Claude Code, Codex, and Cursor each handle it differently. You write the files; the vendor controls discovery.

The ecosystem reflects this. Codex has `AGENTS.md` for persistent context and a separate skills system for actions. Claude Code's skill format distinguishes "reference content" from "task content" with different frontmatter flags. The tools support background knowledge in skills, but the design pressure points toward separation.

## What context-db does

context-db takes the portable parts of skills — front matter, symlinks, standard structure — and applies them to background knowledge, with one key difference: **you control the discovery mechanism**.

A shell script generates `-toc.md` indexes from YAML front matter. Each TOC is a lightweight list of descriptions with paths. An agent reads the TOC, decides what's relevant, and fetches only those documents. Nested folders produce nested TOCs, supporting arbitrarily deep hierarchies — scaling from a handful of documents to hundreds.

The target is large projects with substantial background knowledge: legacy systems with years of accumulated decisions, enterprise services with complex data models, multi-team codebases where no single person holds the full picture. These are the projects where a few hundred lines of context isn't enough, and where an agent needs a map before it can search.

## Is a TOC necessary?

Claude Code has grep and glob. Cursor has RAG. Can't the agent just search?

These are **retrieval** mechanisms — they answer "find me something matching this query." A TOC is a **discovery** mechanism — it answers "here's what exists."

Without a map, the agent must already know what to search for. A grep for "schema" finds schema-related files, but won't surface the deployment constraints or API contracts that might also matter. A TOC at startup gives the agent a complete picture of available knowledge in ~100 tokens, then lets it pull in what it needs.

Anthropic's own engineering blog notes that vector/RAG retrieval "flattens rich structure into undifferentiated chunks, destroying critical relationships" — it wasn't designed for navigating hierarchical knowledge. A TOC preserves structure: the agent sees domains, subdomains, and documents organized the way the team thinks about the system.

For small projects, built-in search is likely sufficient. The TOC becomes essential as projects grow, as knowledge spans multiple domains, and especially when context is shared across projects via symlinks — where the agent has no prior knowledge of what's been linked in.

## Portability

Someone publishes a set of knowledge documents — coding standards, onboarding guides, architecture overviews. Another project symlinks to them:

```bash
ln -s /path/to/shared/coding-standards context-db/coding-standards
```

`build_toc.sh` reads the descriptions and generates a unified TOC, giving the LLM a map into an arbitrary collection of documents regardless of where they live on disk. The build script never writes into symlinked folders.

This is the core portability feature borrowed from skills: self-describing folders that can be composed into larger hierarchies without coordination.
