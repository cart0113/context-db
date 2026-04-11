---
description:
  Maturity status of each subagent mode — ask is 75% (good test results), review
  is 40% (structure done, needs real testing), update-context-db is 10%
---

# Subagent Mode Maturity

Status as of 2026-04-11.

## ask — 75%

Working and getting good test results. The verbatim-snippet output format is
producing useful context. Constrained navigation (TOC + Read) works reliably.
Frequency rules (always/major/never) are implemented and tested.

Remaining work:

- Edge cases with large context-db structures
- Tuning for different model tiers (haiku vs sonnet behavior differences)
- Validation against more diverse project types

## review — 40%

Structure is in place: runs from project root, calls git diff itself, navigates
context-db for conventions, returns a full report on stdout. Scope config
(context-db-only vs context-db-and-general) is implemented.

Remaining work:

- Real-world testing against actual code changes
- Tuning the report format and citation quality
- Testing with different review models
- The commit-first flow needs testing in practice
- Verifying the scope separation produces clean reports

## update-context-db — 10%

Two-phase architecture is designed (update subagent writes, review subagent
checks via diff). The update subagent has Write/Edit tools. The review phase
captures diffs and passes them.

Remaining work:

- Almost everything — this mode has not been tested
- The update subagent's ability to navigate + write correctly
- Quality of the review phase
- Handling of new files vs edits
- Whether the update subagent follows context-db conventions
- The full end-to-end flow (main agent → update → review → evaluate)
