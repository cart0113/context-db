---
description:
  Inlined automatically on every /context-db prompt, right before the user's
  instruction. The handful of rules or pointers the agent should see every time
  it consults the knowledge base.
---

# On Prompt

<!--
Optional, and the ON_* file most projects actually use. Place it at the root of
your context-db/ folder (context-db/ON_PROMPT.md). If it exists, its body is
inlined automatically on every `/context-db prompt`, so it is the freshest thing
in front of the agent when it starts work.

Use it for the few rules the agent should see every single time. Keep it brief —
every line is re-read on every prompt. Delete this comment and replace the
example below with your own. Remove the file entirely if you don't need it.

Two sibling files work identically if you ever need them:
context-db/ON_UPDATE.md (inlined on every `update`) and
context-db/ON_MAINTAIN.md (inlined on every `maintain`). Most projects never add
them.
-->

This is a payments service — PCI-scoped. Before touching anything that handles
card data, storage, or logging, check the project folder for the handling rules;
do not infer them from the code alone.
