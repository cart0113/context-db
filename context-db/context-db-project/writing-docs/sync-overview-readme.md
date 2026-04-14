---
description:
  Three overview documents describe each project — README.md, docs site
  overview, and context-db overview. They share content but serve different
  audiences, have different formats, and must be kept as separate files synced
  manually.
---

## The Three Overviews

| File                                       | Audience                | Format                    | Purpose                                              |
| ------------------------------------------ | ----------------------- | ------------------------- | ---------------------------------------------------- |
| `README.md`                                | Humans on GitHub        | Plain markdown            | First impression, install steps, repo structure      |
| `docs/src/overview/overview.md`            | Humans on the docs site | Plain markdown (docsify)  | Detailed explanation, folder structure, how it works |
| `context-db/<project>-project/overview.md` | LLM agents              | Markdown with frontmatter | Architecture context, design principles              |

All three describe what the project is and how it works. When any of these
change, check the other two.

## Never symlink — must be separate files

context-db overview requires YAML frontmatter; docs/README must not have it. A
symlink forces one format on all three.

## What to sync vs what differs

Sync: project description, feature list, folder structure, setup instructions.
Audience-specific: README has license/quick-start, docs overview has richer
explanation with docsify links, context-db overview has frontmatter and
agent-facing architecture framing.

## Process

No automated sync. After changing any of the three: check the other two for
contradictions, update shared sections, leave audience-specific content alone.
Always re-read the context-db overview's `description` frontmatter after body
changes — the description drives agent routing.
