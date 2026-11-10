---
type: Convention
description:
  README and docs/index.md tell the same story and are updated together; the
  agent-facing overview.md is small, independent, and never a copy of either.
---

# README, docs landing page, agent overview

| File                                       | Audience         | Sync? | Typical size  |
| ------------------------------------------ | ---------------- | ----- | ------------- |
| `README.md`                                | Humans on GitHub | yes   | 100–200 lines |
| `docs/index.md`                            | Docs site        | yes   | 60–120 lines  |
| `context-db/<project>-project/overview.md` | Agents           | no    | 20–40 lines   |

The README is the canonical explainer. The docs landing page is a shorter
version of it that links into the detail pages. When one changes, check the
other for contradictions.

[overview.md](../overview.md) is not a copy of the README. It is what a new
contributor would be told in 30 seconds before touching the code: API surfaces,
what is generated versus hand-edited, what to run after a change. If a section
reads like "what this project is", it is in the wrong file.

The three are separate files, never symlinks: the agent overview needs
frontmatter, and the README must not have it.
