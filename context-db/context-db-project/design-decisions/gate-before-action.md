---
type: Decision
description:
  Why write-command templates (update, maintain) put the null-result decision
  before writing instructions — counters LLM action bias from RLHF
---

LLMs have an action bias: RLHF rewards producing output, so "nothing to do"
feels like failure to the model. When a command like `/context-db update` runs,
the model is primed to write something even when there's genuinely nothing to
persist.

The fix is structural: put the decision ("is there anything worth adding?")
before the instructions ("here's how to write"). If the gate comes after, the
model has already mentally committed to acting.

[update.md](../../../skill/context-db/prompts/update.md) opens with the decision
and names the null result in its first paragraph, before any write mechanics.
[maintain.md](../../../skill/context-db/prompts/maintain.md) does the same: "Check
first, change second", and a one-line stop when nothing needs changing, before
any list of what to fix.
[format.md](../../../skill/context-db/prompts/format.md) stays neutral: it is a
style guide, not a decision point.

When editing these prompts, preserve this ordering. Moving writing
instructions above the decision gate reintroduces the bias.

See also:
[context-delivery-problem.md](../context-db-theory/context-delivery-problem.md)
covers the related "obedience poisoning"
failure mode (model treats background knowledge as directives). Action bias is
distinct — it's about the compulsion to produce output, not about how context is
interpreted.
