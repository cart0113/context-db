---
description:
  Why frequency control matters for the subagent — cost of unnecessary calls,
  why "major" is the right default, edge cases the instructions don't cover
status: deprecated
---

# When to Call the Subagent

## Why frequency control matters

Each subagent call takes 10-30 seconds and costs tokens. A follow-up like "make
that variable name shorter" does not need a fresh knowledge base lookup. The
`when` config (always/major/never) controls this, and `generate_instructions()`
outputs appropriate guidance to the main agent.

## Edge cases the instructions don't fully cover

The generated instructions say "skip follow-ups and small refinements" for
`major` mode, but some edge cases need judgment:

- **Topic change within a task**: "now commit this" after coding work IS a topic
  change — commit standards may differ from coding standards. The subagent
  should fire.
- **Pre-review after user-prompt**: if user-prompt already returned the relevant
  standards, pre-review is redundant for the same task. But if the task scope
  changed, pre-review adds value.
- **Code-review after small fix**: if the main agent made a one-line fix to
  address a code-review finding, re-running code-review is wasteful. The
  instructions say "skip follow-on edits to a major edit" but the agent
  sometimes re-runs anyway.
