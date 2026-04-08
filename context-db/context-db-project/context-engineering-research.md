---
description:
  Research landscape on context engineering for LLM coding agents — how tools
  handle context, structured vs unstructured evidence, and implications for
  context-db
---

# Context Engineering Research Landscape (2024–2026)

## How AI Coding Tools Handle Context

The major AI coding tools use fundamentally different architectures for
providing codebase context to LLMs.

### RAG-Based (Cursor, Windsurf)

**Cursor** indexes the codebase by splitting files into semantic chunks using
AST-based parsing (functions, classes, ~500 token blocks), then converts them to
vector embeddings. When you query with `@Codebase`, it performs semantic search
against this index. The embedding model is trained on actual agent sessions.
Cursor also has `.cursor/rules/` with glob-based scoping and rule types (Always,
Auto Attached, Agent Requested). Their semantic search reportedly improves agent
accuracy by 12.5%.

**Windsurf** uses a proprietary approach called "M-Query." It builds an
AST-based semantic index, indexing code entities (functions, methods, classes)
rather than raw file chunks. Their context assembly pipeline loads rules first,
then persistent Memories from prior sessions, then open files (active file gets
highest weight), then runs M-Query retrieval, then reads recent actions (edits,
terminal commands, navigation history).

### Tool-Based On-Demand (Claude Code)

Claude Code does not pre-index or embed the codebase. It uses tool calls (Bash,
Grep, Glob, Read) to search and read files on demand. It relies on `CLAUDE.md`
files as structured context, `.claude/rules/` for path-specific rules, and
subagents with isolated context windows for delegation. It has a much larger
effective context window (200K tokens, or 1M with Opus), which lets it hold more
code in working memory at once.

### Key Tradeoff

RAG is faster for lookup but can miss context that wasn't well-embedded.
Tool-based retrieval is slower per step but can be more precise and adaptive.
Anthropic's own engineering blog notes that vector/RAG retrieval "flattens rich
structure into undifferentiated chunks, destroying critical relationships."

## Structured vs. Unstructured Context: Evidence

### Chroma's "Context Rot" Research (July 2025)

Testing 18 LLMs including GPT-4.1, Claude 4, and Gemini 2.5:

- Performance grows increasingly unreliable as input length grows
- Even when a model's context window isn't close to full, adding more tokens
  degrades performance
- The "lost-in-the-middle effect" causes 30%+ accuracy drops for information
  positioned in the middle of context
- Attention dilution is quadratic — 100K tokens means 10 billion pairwise
  attention relationships
- Semantically similar but irrelevant content ("distractors") actively misleads
  models

### ETH Zurich Study on AGENTS.md (February 2026)

The most directly relevant experimental evidence:

- LLM-generated context files **reduced** success rates by ~3% compared to no
  context file at all
- Human-written context files offered only a marginal ~4% improvement
- Context files increased inference costs by 20%+ and increased the number of
  agent steps
- Codebase overviews and directory listings did not help agents navigate faster
  — agents are "surprisingly good at discovering file structures on their own"
- Recommendation: omit LLM-generated context files entirely, limit human-written
  instructions to non-inferable details (specific tooling, custom build
  commands)

### Structured Context Benchmarks

- Structured context shows up to +13.0% improvement in task accuracy compared to
  unstructured context
- Key techniques: noise removal (stripping non-essential elements) and
  structural injection (organized snapshots with sections)
- LongCodeZip (2025) achieved up to 5.6x compression with hierarchical
  function-level chunking without sacrificing task performance

## Arguments For Curated Context

- **Martin Fowler (Feb 2026):** CLAUDE.md is "the single most important context
  engineering artifact" — context engineering separates 10x from 2x value
- **Spotify's Honk system (1,500+ merged PRs):** careful context engineering
  essential for reliable, mergeable PRs; different agents need different
  prompting styles
- **HumanLayer's ACE methodology:** handles 300K LOC Rust codebases using
  spec-driven development where specs become source of truth
- **Anthropic's best practices:** "Your CLAUDE.md file should contain as few
  instructions as possible — ideally only ones which are universally applicable"
- **ACE paper (arXiv:2510.04618):** A smaller open-source model (DeepSeek-V3.1)
  using structured, evolving context matched production-level performance, even
  surpassing it on harder splits

## Arguments Against Curated Context

- **ETH Zurich:** context files that are too detailed hurt performance — agents
  are "too obedient" and follow unnecessary instructions
- **Context rot:** even well-structured context consumes tokens that contribute
  to performance degradation
- **Staleness:** code snippets in context files become out-of-date quickly
- **Cost:** context files increase inference costs 20%+ with marginal quality
  benefit
- **Redundancy:** agents can discover project structure, build commands, and
  file layouts on their own

## Emerging Consensus

Curated context files are valuable **only when they contain information the
agent genuinely cannot infer on its own**. High-value content: custom build
commands, non-obvious architectural decisions, team-specific conventions,
unusual tooling. Low-value or counterproductive: directory listings, generic
best practices, obvious patterns.

## Smaller Models and Structured Context

Direct evidence is limited but suggestive:

- **ACE paper (ICLR 2026):** DeepSeek-V3.1 with structured context matched
  larger production-level models — strongest evidence that structured context
  closes the gap between small and large models
- **Chroma's research:** smaller models (GPT-3.5-Turbo) exhibit greater
  performance degradation (>20%) from lost-in-the-middle effect, suggesting they
  are more sensitive to how context is structured
- **LangChain:** multi-agent isolation benefits all model sizes, but
  proportionally larger for models with smaller effective context windows

General pattern: weaker models are more easily overwhelmed by irrelevant
context, more susceptible to distractor interference, and more likely to follow
bad instructions. They benefit more from _precise, minimal_ structured context,
but also suffer more from _verbose, redundant_ context.

## TOC-Style Hierarchical Context

No published benchmarks directly compare TOC-style hierarchical context to flat
context for LLM codebase navigation. Related approaches:

- **Graph-based code navigation** (LOCAGENT, CodexGraph) — parses codebases into
  graph representations with hierarchical dependency structures, outperforming
  flat search on code localization tasks
- **LongCodeZip** — two-level hierarchy (function-level chunking + block-level
  pruning) achieving 5.6x compression without performance loss
- **MemGPT** — OS-inspired hierarchical memory (main context + archival + recall
  storage), analogous to a TOC that decides what to page in
- **Anthropic's subagent research** — subagents with isolated, narrowly-scoped
  contexts outperformed single agents with broad context
- **ETH Zurich counterpoint** — codebase overviews and directory listings
  (simple TOCs) did not help agents navigate faster

Implication: an **agent-navigable TOC** that lets the agent decide what to load
is likely more valuable than a **pre-loaded TOC** that dumps structure into
context. The value is in enabling selective loading, not in the TOC document
itself.

## Context Window Utilization

- Models hit a performance ceiling around 1M tokens regardless of advertised
  window size (SWE-rebench data)
- Accuracy drops 10–20+ percentage points when relevant info sits in the middle
  of long contexts
- Claude Code uses 5.5x fewer tokens than Cursor for equivalent tasks, partly
  due to better context management
- HumanLayer recommends keeping context utilization in the 40–60% range through
  frequent intentional compaction

Practical strategies: subagent isolation, observation masking (hiding verbose
tool output), rolling compression, tool-based retrieval over pre-loading,
.claudeignore.

## Implications for context-db

1. **Agent-navigable TOCs are the right pattern.** Letting the agent decide what
   to read based on descriptions is better than dumping everything. This is what
   `context-db-generate-toc.sh` + description-based filtering does.

2. **Descriptions are the critical mechanism.** The ETH Zurich study says agents
   waste tokens on irrelevant pre-loaded structure. context-db's
   descriptions-as-filter approach is closer to the "load on demand" pattern
   that Anthropic recommends.

3. **Minimal, high-signal content only.** Anthropic's guidance, ETH Zurich, and
   the context rot research all converge: less is more. Only include what the
   agent cannot infer from the code.

4. **Strongest use case is large codebases** where full RAG indexing is
   impractical or where the project has non-obvious architectural decisions that
   semantic search would not surface.

5. **Risk to test for:** if context documents contain information agents could
   discover on their own (file structure, obvious patterns), they consume tokens
   that degrade performance.

6. **Smaller models may benefit disproportionately** from the progressive
   disclosure pattern, since they are more sensitive to context noise.

## Sources

- [Spotify: Context Engineering (Honk, Part 2)](https://engineering.atspotify.com/2025/11/context-engineering-background-coding-agents-part-2)
- [Martin Fowler: Context Engineering for Coding Agents](https://martinfowler.com/articles/exploring-gen-ai/context-engineering-coding-agents.html)
- [Chroma Research: Context Rot](https://research.trychroma.com/context-rot)
- [ETH Zurich / InfoQ: Value of AGENTS.md Files](https://www.infoq.com/news/2026/03/agents-context-file-value-review/)
- [MarkTechPost: ETH Zurich on AGENTS.md](https://www.marktechpost.com/2026/02/25/new-eth-zurich-study-proves-your-ai-coding-agents-are-failing-because-your-agents-md-files-are-too-detailed/)
- [Morph: Context Engineering: Why More Tokens Makes Agents Worse](https://www.morphllm.com/context-engineering)
- [Factory.ai: The Context Window Problem](https://factory.ai/news/context-window-problem)
- [HumanLayer: Advanced Context Engineering](https://github.com/humanlayer/advanced-context-engineering-for-coding-agents)
- [ACE Paper (arXiv:2510.04618)](https://arxiv.org/abs/2510.04618)
- [LongCodeZip (arXiv:2510.00446)](https://arxiv.org/html/2510.00446v1)
- [Cursor Docs: Codebase Indexing](https://cursor.com/docs/context/codebase-indexing)
- [Windsurf Docs: Context Awareness](https://docs.windsurf.com/context-awareness/overview)
- [LangChain: Context Engineering in Agents](https://docs.langchain.com/oss/python/langchain/context-engineering)
- [Engineer's Codex: Your Agents.md Might Be Making AI Worse](https://www.engineerscodex.com/agents-md-making-ai-worse)
- [JetBrains Research: Smarter Context Management](https://blog.jetbrains.com/research/2025/12/efficient-context-management/)
- [Lance Martin: Context Engineering for Agents](https://rlancemartin.github.io/2025/06/23/context_engineering/)
- [Anthropic: Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
