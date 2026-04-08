---
description:
  Three overview documents describe context-db — README.md, docs site overview,
  and context-db overview. They share content but serve different audiences and
  must be kept in sync manually.
---

## The Three Overviews

| File                                        | Audience                | Purpose                                              |
| ------------------------------------------- | ----------------------- | ---------------------------------------------------- |
| `README.md`                                 | Humans on GitHub        | First impression, install steps, repo structure      |
| `docs/src/overview/overview.md`             | Humans on the docs site | Detailed explanation, folder structure, how it works |
| `context-db/context-db-project/overview.md` | LLM agents              | Design principles, what context-db is and is not     |

All three describe what context-db is, why it exists, and the folder structure
convention. When any of these change, check the other two.

## What to sync

- The "what is context-db" description and value proposition.
- The folder structure diagram — appears in README.md and the docs overview.
- The wiring instructions (skill + rule).
- Private/public folder behavior.

## What differs

Each file has content unique to its audience:

- **README.md** — repo structure section, license, getting started steps.
- **Docs overview** — comparison to Obsidian, Reddit anecdote about skill count,
  link context within the docs site.
- **Context-db overview** — core design principles section, "what it is not"
  section targeted at agents.

## Folder Structure Convention

`writing-docs/` always lives inside the main project folder (e.g.,
`context-db/context-db-project/writing-docs/`), never parallel to it. Folders
parallel to the project folder are reserved for project-agnostic content —
symlinked standards like `coding-standards/`, `writing-standards/`, and
`agent-behavior/`.

## Process

There is no automated sync. After changing any of the three files:

1. Open the other two and check for contradictions or stale content.
2. Update shared sections (description, folder structure, wiring) to match.
3. Leave audience-specific sections alone unless the underlying facts changed.
