[maintain-instructions]

Target: {target_path}

Before starting, ask the user how they want to run this:

1. **Guided** — stop after each phase, wait for input
2. **Review** — run all phases, report findings, don't change without approval
3. **Autonomous** — run all phases, fix what's clear, summarize + ask on
   ambiguity

Wait for their answer before proceeding.

Phase 1 — Structural health: 5-10 items per folder, 50-150 lines per file, 2-3
levels deep max. Split oversized files/folders, merge tiny ones, fill missing
folder descriptors, sharpen vague descriptions.

Phase 2 — Content freshness: Use git log and git diff. Verify referenced
files/functions still exist. Fix outdated content directly.

Phase 3 — Content value: Cut anything the agent could learn faster by reading
project assets. Code summaries, property lists, module layouts, step-by-step
instructions.

Phase 4 — Coverage gaps: Check recent git history for corrections, reverts,
pitfalls. Add only genuinely non-obvious entries.

Phase 5 — Documentation drift: Compare context-db against project docs. Where
they disagree, trust the project assets.

Phase 6 — Cross-references: Fix broken "See also" links. Add new ones only where
genuinely helpful.

Phase 7 — Reindex: Re-read every file, update all description fields to match
current content. Work bottom-up (deepest folders first). Run TOC on every
changed folder.

The default posture is to cut. An audit should leave context-db smaller and
sharper, not larger.

Do not run /context-db maintain yourself. The user invokes this.

[end maintain-instructions]
