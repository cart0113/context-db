---
description:
  The context-db standard — overview, design decisions, and context engineering
  research
---

context-db is a standard for organizing project knowledge as hierarchical
Markdown with on-demand TOC generation, so LLM agents can discover and fetch
only what they need. Start with `overview.md` for the core design principles.
`context-db-generate-toc-sh.md` explains how the TOC script parses frontmatter.
`cross-project-sharing.md` covers symlinks, submodules, and git-sync for sharing
context across repos. `design-decisions/` documents format, naming, and tooling
choices. `context-engineering-research.md` surveys the research landscape on
structured context for coding agents.
