---
description:
  Maturity status of each subagent mode — pre-review is 30% (newly added,
  initial design done), user-prompt is 75% (good test results), code-review is
  40% (structure done, needs real testing), update-context-db is 25%
  (single-phase, initial tests working)
---

# Subagent Mode Maturity

Status as of 2026-04-11.

## pre-review — 30%

Newly added. The agent sends a structured plan (type/language/size) and the
subagent returns verbatim applicable standards. Default model: haiku. The
combined workflow in instructions mode wires pre-review and code-review into a
single numbered sequence.

Remaining work:

- Real-world testing to verify standards recall quality
- Tuning the structured plan format — what fields give the subagent enough
  signal to pick the right standards
- Verifying haiku compliance (returns standards, does not help with the task)
- Testing the combined workflow instructions across different enabled/disabled
  configurations

## user-prompt — 75%

Working and getting good test results. The verbatim-snippet output format is
producing useful context. Constrained navigation (TOC + Read) works reliably.
Frequency rules (always/major/never) are implemented and tested.

Remaining work:

- Edge cases with large context-db structures
- Tuning for different model tiers (haiku vs sonnet behavior differences)
- Validation against more diverse project types

## code-review — 40%

Structure is in place: runs from project root, calls git diff itself, navigates
context-db for conventions, returns a full report on stdout. Review-type config
(context-db vs full) is implemented.

Remaining work:

- Real-world testing against actual code changes
- Tuning the report format and citation quality
- Testing with different review models
- The commit-first flow needs testing in practice
- Verifying the review-type separation produces clean reports

## update-context-db — 25%

Single-phase: subagent receives developer's notes, runs `git diff`, navigates
context-db, and edits/writes files directly from the project root. No separate
review phase — the main agent reviews the reported changes. Initial tests are
working (this knowledge base update was made by the subagent itself).

Remaining work:

- Quality and accuracy of edits across diverse project types
- Whether the subagent correctly prioritizes what to file vs. skip
- Handling of new files vs. edits to existing files
- Testing with varied developer notes (sparse vs. detailed)
- Whether the "only file what code can't tell you" rule is followed reliably
