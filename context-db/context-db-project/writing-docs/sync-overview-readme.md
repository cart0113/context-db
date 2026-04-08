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

## These must be separate files — never symlink

The context-db overview requires YAML frontmatter (`description:` field) for the
TOC system. Docs files (docsify) and README.md must NOT have frontmatter. A
symlink forces them to be the same file, which means either:

- The docs file gets frontmatter it shouldn't have, or
- The context-db file loses its frontmatter and breaks the TOC.

**Always keep these as three independent files.** They share content but differ
in format, audience, and structure.

## What to sync

- The "what is this project" description and feature list.
- Folder structure diagrams.
- Setup/install instructions.
- Key behavioral descriptions.

## What differs

Each file has content unique to its audience:

- **README.md** — license, quick-start, links to live docs, repo structure.
- **Docs overview** — rendered in docsify, links to other doc pages, richer
  explanations for humans browsing the site.
- **Context-db overview** — frontmatter with description, architecture framing
  for agents, design decisions, "what it is not" constraints.

## Folder Structure Convention

`writing-docs/` always lives inside the main project folder (e.g.,
`context-db/<project>-project/writing-docs/`), never parallel to it. Folders
parallel to the project folder are reserved for project-agnostic content —
symlinked standards like `coding-standards/`, `writing-standards/`, and
`agent-behavior/`.

## Process

There is no automated sync. After changing any of the three files:

1. Open the other two and check for contradictions or stale content.
2. Update shared sections to match.
3. Leave audience-specific sections alone unless the underlying facts changed.
4. **Re-read the context-db overview and update its `description` frontmatter.**
   The `description` field is how agents decide whether to open the file — it
   must accurately summarize the current content. Every time the overview body
   changes, read the file and rewrite the description to match. Do not assume
   the old description is still correct.
