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
`skill/context-db/prompts/` with a MyST `literalinclude` directive. Editing a
prompt changes the docs on the next build; there is no generator script and
nothing to regenerate.

Pages about user intent (worked examples, when to use which command, setup)
stay hand-written.
