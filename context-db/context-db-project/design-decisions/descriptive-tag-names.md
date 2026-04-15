---
description:
  Section tags must be descriptive and self-documenting —
  [spawn-context-db-lookup] not [instructions],
  [sub-agent-navigation-constraints] not [rules]
---

Tags like `[instructions]` or `[rules]` are too generic. A tag should tell you
what the block does at a glance without reading its contents.

Good: `[spawn-context-db-lookup]`, `[sub-agent-output-format]`,
`[prompt-user-instructions]`, `[context-db-findings]`

Bad: `[instructions]`, `[rules]`, `[output]`, `[response]`

When a tag appears in the agent's context, it competes with every other tag for
attention. Generic names force the model to read the block to understand its
purpose. Descriptive names let it skip irrelevant blocks and locate what it
needs.
