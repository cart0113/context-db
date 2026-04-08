---
name: bruha-audit-docs
description: >-
  Audit user-facing docs against the actual code — find stale content, deleted
  features, broken references, and drift between docs and implementation. Uses
  git diff, code, and context-db as sources of truth.
argument-hint: '[docs-path]'
allowed-tools: Read Write Edit Glob Grep Bash Agent
---

## What this does

Audit the project's **user-facing documentation** (docs site, README, guides)
against the actual codebase. Find problems — stale instructions, references to
deleted code, drift between what the docs say and what the code does — and fix
them collaboratively with the user.

This is NOT an audit of context-db. Context-db is for agents; docs are for
people. You will _read_ context-db for ground truth, but you are _auditing_
docs.

## Target

If `$ARGUMENTS` is provided, treat it as the docs path to audit (e.g.
`docs/src/configuration/`). Audit that path and its children.

If no argument is provided, audit all documentation: `docs/`, `README.md`, and
any other user-facing markdown files at the project root.

## Before you start — gather context

You must understand the project before you can judge its docs. Do all of these
before auditing:

### 1. Read the project knowledge base

If a `context-db/<project-name>-project/` folder exists, **read it in its
entirety** — every file, every subfolder. This is your primary source of truth
for how the project works, its architecture, conventions, and design decisions.

### 2. Read writing standards

If a `context-db/writing-standards/` folder exists, or any markdown files about
writing style, **read them in full**. You must follow the project's voice, tone,
and formatting conventions when proposing doc edits.

Also check `context-db/using-bruha/` or any folder that describes how docs
content should be structured.

### 3. Check git for recent changes

```bash
# What changed recently in the codebase?
git log --oneline --since="4 weeks ago" --name-only 2>/dev/null

# What's changed but not yet committed?
git diff --name-only 2>/dev/null
git diff --cached --name-only 2>/dev/null

# If a base branch is available, what diverged?
git diff main --name-only 2>/dev/null
```

This tells you what code has changed and may have made docs stale.

### 4. Read the docs

Read every doc file in scope. For each file, note what it claims about the
project — features, configuration options, commands, file paths, behavior.

## Audit phases

Work through these in order. **Be very chatty** — explain what you're finding,
what looks good, what looks wrong, and why. Ask for feedback and guidance
frequently. Docs are high-visibility and opinionated — the user should be in the
loop on every non-trivial change.

### Phase 1: Dead references

The most important phase. Find things the docs reference that no longer exist in
the code:

- **Deleted files or directories** — docs mention a path that doesn't exist
- **Removed functions, classes, or config keys** — docs describe behavior that
  the code no longer supports
- **Dead commands** — docs tell users to run something that no longer works
- **Broken links** — internal doc links that point to missing pages

For each finding, check whether the feature was removed, renamed, or moved. Use
`git log` on the specific file to understand what happened.

**Fix glaring problems directly** — if the code clearly no longer has a feature
and the docs describe it, remove or update that section. Tell the user what you
changed and why.

**Ask about ambiguous cases** — if you're not sure whether something was removed
intentionally or is just temporarily broken, ask before editing.

### Phase 2: Accuracy check

For docs that reference things that DO exist, verify they're described
correctly:

- **Config options** — are defaults, types, and descriptions accurate?
- **Behavior descriptions** — does the code actually do what the docs say?
- **Code examples** — do they match current APIs and patterns?
- **Screenshots or diagrams** — flag if they might be outdated (you can't verify
  visually, but mention them)

Cross-reference against context-db entries for the same topics. If context-db
and docs disagree, check the code to determine which is right.

Report what you find. Propose fixes for inaccuracies and **wait for user
confirmation** before applying non-obvious corrections.

### Phase 3: Coverage gaps

Look for features or behaviors that exist in the code but aren't documented:

- New config options with no docs page
- Features added in recent commits with no corresponding doc update
- Behavior that context-db describes but user docs don't cover

**Don't just list gaps** — for each one, tell the user what you'd write and
where you'd put it. Ask whether they want you to draft it.

### Phase 4: Quality and consistency

A lighter pass on writing quality:

- **Tone consistency** — does the writing style match across pages? Does it
  follow writing-standards if defined?
- **Formatting** — are headings, code blocks, and lists used consistently?
- **Organization** — is information easy to find? Are pages too long or too
  short?
- **Duplication** — is the same information explained in multiple places? (If
  so, which should be the canonical source?)

This phase is advisory. Report findings and let the user decide what to fix.

## Interaction style

**Be very chatty.** Talk through what you're doing and finding. This is a
conversation, not a report. Explain your reasoning so the user can correct your
understanding.

**Ask for feedback often.** After each phase, summarize what you found and ask:
"Does this match your understanding? Anything I'm missing? Should I proceed with
these fixes?"

**Ask for guidance before writing.** When you're about to update a doc, describe
what you plan to change and why. Wait for a thumbs-up before editing — unless
the problem is unambiguously wrong (e.g., referencing a file confirmed deleted
from the repo).

**Point out what's good.** If a doc page is well-written, accurate, and
complete, say so. The audit isn't just about finding problems.

**Respect the user's voice.** Docs are for humans. They have personality, tone,
and style choices that matter. Don't flatten everything into generic technical
writing. If writing standards exist, follow them. If not, match the existing
voice.

## When making edits

1. Always read the file before editing.
2. Make minimal, targeted changes — don't rewrite paragraphs that are fine.
3. If writing-standards exist, follow them for any new or rewritten content.
4. After editing, show the user what changed and ask if it reads well.
5. Never delete a doc page without explicit permission — flag it as potentially
   unnecessary and let the user decide.

## Summary

After all phases, provide a brief summary:

- What was fixed
- What needs the user's attention
- What's in good shape
- Any open questions

Keep the summary short — the real value was in the conversation along the way.
