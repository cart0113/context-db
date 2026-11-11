---
type: Convention
description:
  README and docs/index.md tell the same story and are updated together; the
  agent-facing overview.md is small, independent, and never a copy of either.
---

# README, docs home page, agent overview

| File                                       | Audience         | Sync? | Typical size  |
| ------------------------------------------ | ---------------- | ----- | ------------- |
| `README.md`                                | Humans on GitHub | yes   | 150–200 lines |
| `docs/index.md`                            | Docs site        | yes   | 100–200 lines |
| `context-db/<project>-project/overview.md` | Agents           | no    | 20–40 lines   |

The README and the docs home page share their opening, "Install", "What it is",
the four commands, "A typical session", and "Why it works this way" almost word
for word. When one changes, change the other. The home page uses cards and tabs
where the README uses a table and a tree. The README's Install section also
carries the steps themselves, because the install prompt sends agents there.

[overview.md](../overview.md) is not a copy of the README. It is what a new
contributor would be told in 30 seconds before touching the code: API surfaces,
what is generated versus hand-edited, what to run after a change. If a section
reads like "what this project is", it is in the wrong file.

The three are separate files, never symlinks: the agent overview needs
frontmatter, and the README must not have it.
