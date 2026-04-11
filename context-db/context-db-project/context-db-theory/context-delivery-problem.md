---
description:
  Why providing context to agents often hurts performance — three distinct
  failure modes (attention dilution, obedience poisoning, memory corruption) and
  what each requires to fix
---

# The Context Delivery Problem

## The paradox

Real projects need agents to know things: conventions, architectural decisions,
domain knowledge, pitfalls. But research consistently shows that providing this
knowledge often makes agents perform worse. The ETH Zurich study (Feb 2026)
found LLM-generated context files _reduced_ success rates by ~3%. Even
human-written context only improved results by ~4% while increasing costs 20%+.

This is not one problem. It is three distinct failure modes that look the same
from the outside but require different solutions.

## Failure mode 1: Attention dilution

Transformer attention is quadratic. At 100K tokens the model maintains 10
billion pairwise attention relationships. At 1M tokens, a trillion. Every token
of context doesn't just take up space — it actively degrades the model's ability
to attend to the tokens that matter.

Chroma's "context rot" research (July 2025, 18 LLMs tested) found:

- Performance degrades at every input length increment, not just near the limit
- 30%+ accuracy drop from the lost-in-the-middle effect
- Semantically similar but irrelevant content ("distractors") actively misleads
- A model with a 1M-token window still rots at 50K tokens

This explains why agents with more context take more turns — they aren't being
more thorough, they're being more distracted. More things to attend to means
more things get attended to, whether or not they help.

**This is a model architecture problem.** No amount of better context
engineering fixes quadratic attention. The fix is either better architectures
(sparse attention, retrieval that doesn't stuff the window) or better isolation
(subagents — Chroma found 90% improvement).

## Failure mode 2: Obedience poisoning

The most counterintuitive finding. The ETH Zurich study found agents are "too
obedient" — when context mentions `uv`, agents use it 1.6x more, even when it's
wrong. When given architectural overviews, agents follow the overview instead of
reading actual code.

The mechanism: models treat all context as _instructions_ rather than
_background knowledge_. There is no "FYI" register in current models. Everything
in the prompt is either ignored or treated as a directive.

This means even _correct, non-redundant_ context can constrain the model's
search space harmfully. Telling a model "the dependency resolution loop uses
cache keys structured as X" doesn't just inform — it anchors. The model stops
exploring alternative interpretations because you've told it the answer.

This is why seemingly banal context can stop an agent from doing as good a job
as without any background knowledge. The context narrows what the model
considers, and sometimes the right answer is outside that narrowed space.

**This is a prompting/framing problem.** The fix isn't less context, it's
context delivered differently — as reference material rather than instructions.
But current models don't distinguish between the two. See:
[subagent-context-delivery.md](other/subagent-context-delivery.md) for one
potential architectural fix.

## Failure mode 3: Memory corruption and self-reinforcement

The Claude Code source leak (March 2026) revealed a three-layer memory
architecture with an `autoDream` subagent that consolidates memory nightly. The
fundamental problem: the model re-ingests its own outputs as trusted facts.

A model writes a slightly wrong observation to memory. Next session, it reads
that back as ground truth. It builds on it. The error compounds. This is
"context poisoning" — and it applies to any persistent memory system, including
manually curated ones.

This is the mechanism behind the "good first pass, stalls long-term" pattern.
Fresh agents solve things stuck agents can't — not because they lack project
knowledge, but because they lack 200 turns of failed approaches anchoring their
thinking. The accumulated _conversation history_ is more toxic than accumulated
_project context_.

**This is a systems architecture problem.** Fixes: external verification of
stored context, expiry/decay mechanisms, human curation, and — critically —
separating project knowledge (survives across sessions) from working memory
(must be discarded).

## What this means for context-db

context-db's design already addresses several of these:

- **On-demand loading via TOC** mitigates attention dilution — the agent reads
  10 descriptions and skips 9 folders instead of ingesting everything
- **"Only include what the agent can't infer"** is the right principle for
  obedience poisoning, though enforcement is hard
- **Human curation** catches memory corruption that automated systems miss

Weaknesses that remain:

- **No per-entry effectiveness testing.** You can't know whether a specific
  context entry helps or hurts without expensive ablation testing. Harmful
  entries persist until someone notices.
- **Content is still treated as instructions.** Even well-framed context-db
  entries anchor the model. There is no way to mark content as "background,
  trust code over this if they conflict."
- **The system rewards comprehensiveness, but performance rewards minimalism.**
  Every instinct says add more. The research says add less.

## Evidence from production systems

The Claude Code source leak (March 2026) provides direct evidence that current
harnesses suffer from these failure modes in practice:

- **Skill descriptions are loaded into the main agent's context.** Every skill's
  name and one-line description sits in the system prompt (~100 tokens each).
  Full SKILL.md content loads into the main window on trigger — no subagent
  isolation.
- **CLAUDE.md is injected as a system-reminder in a user message,** not the
  system prompt. But it's still in the main conversation context, subject to all
  three failure modes.
- **System-reminders re-inject repeatedly.** Issue #17601: one user documented
  10,577 hidden system-reminder injections over 32 days, consuming 15-30% of the
  context window. Issue #27599: infinite re-injection in headless mode.
- **The ToolSearch experiment failed.** v2.1.69 deferred ALL built-in tool
  schemas behind on-demand loading. The model stopped reliably finding tools it
  needed. Partially reverted in v2.1.72. This is the serendipity problem at
  scale — hiding things behind on-demand loading means agents miss things they
  don't know to look for.
- **Claude Code names this problem.** "Context entropy" — the gradual
  degradation of agent performance in long-running sessions. Five compaction
  strategies and an `autoDream` nightly consolidation process are
  countermeasures.

**If subagent isolation is better for context delivery, then the harnesses
should work this way natively.** The fact that Claude Code loads context into
the main window — and documents the resulting problems — suggests this is a
platform limitation, not something individual projects should work around.

## What needs to change at the model/harness level

1. **A "reference" vs "instruction" distinction in prompts.** Context tiers
   where the model knows "this is background knowledge, not directives."
   OpenAI's Instruction Hierarchy paper (2024) establishes tool outputs at
   lowest authority (Priority 30) vs system messages at highest (Priority 0).
   But this is a binary security distinction, not a nuanced "treat this as
   background" signal.
2. **Context scoring in harnesses.** Track which context entries agents actually
   use vs. ignore, and prune automatically.
3. **Confidence/freshness metadata that models respect.** Train models to weight
   context by reliability signals, not just position. Research on positional
   bias shows primacy degrades past 50% context fill; recency stays stable.
4. **Subagent isolation as default architecture.** Give each subtask a fresh
   agent with only the relevant context slice. But the ToolSearch revert shows
   this trades obedience poisoning for serendipity loss.
5. **Proactive compaction against the 35-minute wall.** All agents degrade after
   ~35 minutes. Either compact proactively or reset working memory while
   retaining project knowledge.

## The core tension

Without context, you get what the model was trained on — impressive first
passes, generic patterns, no project-specific knowledge. With context, you get
anchoring, distraction, and obedience. The current generation of models cannot
hold project knowledge without being constrained by it.

This is not a tooling problem with a tooling fix. It is a fundamental limitation
of how current transformer architectures process context. Better tools
(including context-db) can reduce the damage. But the problem won't be solved
until models can distinguish "things I should know" from "things I should do."

## See also

- [context-engineering-research.md](../context-engineering-research.md) — full
  research landscape with sources and citations
- [subagent-context-delivery.md](other/subagent-context-delivery.md) — subagent
  architecture as a potential delivery mechanism
- [why-hierarchy-works.md](why-hierarchy-works.md) — how hierarchy reduces token
  load via progressive disclosure
