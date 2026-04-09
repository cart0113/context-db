---
description:
  Cross-references — lateral links across the hierarchy, and what we rejected
  from knowledge graph research
---

## The problem

A tree has no lateral edges. If error-handling guidance lives in
`coding-standards/` and an agent navigates `agent-behavior/`, it won't discover
the related document. Cross-cutting concerns are invisible from the wrong
starting point.

## The fix

"See also" links at the bottom of document bodies. Not in frontmatter (bloats
the TOC), not in a separate graph file (second source of truth). Just markdown
in the body — zero TOC tokens, only read when the file is already open.

## What we rejected and why

- **Tags.** Vocabulary maintenance cost exceeds retrieval benefit (Forte). The
  description field already functions as a free-text tag.
- **Typed relationships** ("depends-on", "extends"). Maintenance scales
  quadratically. Not worth it at <100 documents.
- **Faceted classification.** Multiple dimensions per document. Overkill at this
  scale.
- **Full knowledge graphs** (Graphify, etc.). Solve a different problem —
  synthesizing large external corpora. A see-also line IS a graph edge.
- **Maps of Content.** Hand-curated cross-cutting index pages. Revisit if
  context-db grows past ~100 documents.
