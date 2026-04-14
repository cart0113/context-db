---
description:
  Why write-command templates put the null-result decision before writing
  instructions — counters LLM action bias from RLHF
---

LLMs have an action bias: RLHF rewards producing output, so "nothing to do"
feels like failure to the model. When a command like `/context-db update` runs,
the model is primed to write something even when there's genuinely nothing to
persist.

The fix is structural: put the decision ("is there anything worth adding?")
before the instructions ("here's how to write"). If the gate comes after, the
model has already mentally committed to acting.

`update-general.md` puts the null-result path in the second sentence, before any
write mechanics load. `write-content-guide.md` stays neutral (it's a style
guide, not a decision point). `maintain-instructions.md` distinguishes between
cutting bloat and preserving real knowledge.

When editing these templates, preserve this ordering. Moving writing
instructions above the decision gate reintroduces the bias.

See also: context-delivery-problem.md covers the related "obedience poisoning"
failure mode (model treats background knowledge as directives). Action bias is
distinct — it's about the compulsion to produce output, not about how context is
interpreted.
