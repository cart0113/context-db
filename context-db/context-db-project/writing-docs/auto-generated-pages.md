---
type: Convention
description:
  Docs that show agent-facing text include the prompt files verbatim with
  literalinclude instead of paraphrasing them, so the docs cannot drift from
  what the agent actually reads.
---

# Include agent-facing text, never paraphrase it

When a docs page would restate what the agent reads, include the source file.
[docs/commands.md](../../../docs/commands.md) pulls each file from
`skill/context-db/prompts/` with a MyST `literalinclude` directive, inside a
dropdown so that the page stays short. Editing a prompt changes the docs on the
next build; there is no generator script and nothing to regenerate.

The plain-language summary above each dropdown ("What the agent does") is
hand-written. When a prompt changes what the agent does, update that summary
too.

Pages about user intent (worked examples, when to use which command, setup)
stay hand-written.
