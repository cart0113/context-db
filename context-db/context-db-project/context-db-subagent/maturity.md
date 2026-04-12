---
description:
  Maturity status of each subagent mode — user-prompt at 75%, others early
  stage. Only user-prompt is enabled by default.
---

# Subagent Mode Maturity

Status as of 2026-04-12.

## user-prompt — 75% (enabled by default)

Working well. Verbatim-snippet output produces useful context. Constrained
navigation is reliable. Now also returns applicable standards based on prompt
intent.

Remaining: edge cases with large context-db structures, tuning across model
tiers, validation against more project types.

## pre-review — 30% (off by default)

Initial design done. Needs real-world testing to verify standards recall quality
and haiku compliance. The combined workflow (pre-review → edit → code-review)
needs testing across different enabled/disabled configurations.

## code-review — 40% (off by default)

Structure in place. Needs real-world testing against actual code changes, tuning
report format, and verifying review-type separation produces clean reports.

## update-context-db — 25% (off by default)

Single-phase design working in initial tests. Needs testing across diverse
project types and varied developer notes. Whether "only file what code can't
tell you" is followed reliably is unverified.
