---
description:
  Why hierarchical folders give O(log n) lookup — Hick's Law, progressive
  disclosure, information foraging, and description quality
---

## The core claim

A hierarchy of folders with 5–10 items each gives logarithmic search time. An
agent reads a short list, picks the best match, and drills down. For 50
documents across 3 levels, that's ~15–20 descriptions read instead of 50.

This isn't novel — it's well-studied under multiple names.

## The theory

**Hick's Law** (1952): Decision time increases logarithmically with the number
of choices. 5–10 items per folder keeps each decision fast. One of the most
replicated findings in cognitive science — applies to LLM attention the same
way.

**Progressive disclosure** (Rosenfeld & Morville, _Information Architecture_):
Show only what's needed at each level. The TOC script surfaces descriptions
first; the agent never loads content it didn't ask for.

**Information foraging theory** (Pirolli & Card, PARC): Agents follow
"information scent" — cues that predict whether a path leads to relevant
content. The `description` frontmatter fields are engineered scent.

## Description quality matters disproportionately

The descriptions are the index entries. A bad description is a broken index
entry — the agent skips a relevant document or opens an irrelevant one.

Include alternative terms when a topic has multiple names. A description like
"How to handle rate limiting (throttling, backpressure, retry logic)" lets the
agent match on any of those terms when scanning the TOC. This is what library
science calls a "synonym ring" — zero cost, better recall.
