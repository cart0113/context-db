---
name: context-db-full-audit
description: >-
  Full audit — audit against project code, docs, and git history for stale
  entries, missing topics, structural problems, cross-references, and doc drift,
  then reindex all descriptions. TRIGGER when: user asks to review or audit the
  knowledge base, or after major project changes.
argument-hint: '[folder-path]'
allowed-tools: Read Write Edit Glob Grep Bash
---

## What this does

Audit the knowledge base against **all** project sources of truth — code, docs,
README files, git history, and configuration — then reindex descriptions to
match.

## Mission

Build a knowledge base that lets an agent produce correct code changes on the
first try with the minimum context window. Every audit decision — what to add,
cut, restructure, or rewrite — is measured against this: does it help an agent
get to the right answer faster, or is it noise?

## Target

If `$ARGUMENTS` is provided, treat it as the folder to audit (e.g.
`context-db/coding-standards/`). Audit that folder and its subfolders.

If no argument is provided, audit the entire `context-db/` directory.

## External symlinks — do NOT follow

context-db folders often contain symlinks to shared standards from other repos.
**Never follow, read, edit, or audit files that resolve outside this project.**
They are owned by another repo and must not be modified here. Symlinks that
resolve within this project are fine.

Use the listing script (not Glob) to discover files — it filters out external
symlinks automatically:

```
.claude/skills/context-db-full-audit/scripts/context-db-list-files.sh <target-path>
```

## Audience

The primary audience for context-db is LLM agents, though it should be useful
for humans too. Every description and every document must help an agentic system
get up to speed on the project using the smallest context window possible. Every
word costs tokens. When evaluating content freshness, coverage gaps, and
description quality, judge everything through this lens — include what an agent
cannot infer from the code, omit what it can.

## Before you start — ask the user

Before doing any audit work, ask the user how they want to run this:

> I can run this audit at different levels of involvement:
>
> 1. **Guided** — I stop after each phase, report findings, and wait for your
>    input before moving on.
> 2. **Review** — I run all phases and report what I found, but don't change
>    anything without your approval.
> 3. **Autonomous** — I run all phases, fix what's clearly wrong, and give you a
>    summary at the end with questions on anything ambiguous.
>
> Which do you prefer?

**Wait for their answer.** Do not proceed until they respond.

- **Guided**: after each phase, present findings, then **stop and wait** for the
  user to respond before starting the next phase.
- **Review**: run all phases back-to-back, report everything found, but make no
  changes. Present proposed fixes for the user to approve.
- **Autonomous**: run all phases back-to-back, fix clear issues, collect
  ambiguous questions for a single summary at the end.

## Audit phases

Work through these phases in order. Be conversational — explain what you're
finding as you go.

**IMPORTANT — pacing:** In Guided mode, each phase ends with a summary and
questions. You MUST wait for the user's response before starting the next phase.
Do not ask a question and then answer it yourself in the same turn.

### Phase 1: Structural health

Enforce logarithmic progressive disclosure — each folder level should halve the
search space so agents navigate a decision tree, not scan a flat list.

**Target: 5–10 items per folder.** This is the core structural invariant.
Actively restructure to achieve it — create subfolders, merge sparse folders,
flatten deep nesting. The goal is a tree where an agent reaches any document in
3–4 decisions.

- **Too many items (>10 children):** Split into subfolders that give agents a
  meaningful branching decision at each level. Propose the reorganization and
  ask before making changes.
- **Too few items (1–2 files):** Merge upward into the parent folder.
- **Too deep (>3–4 levels):** Flatten. Wide and shallow beats narrow and deep.
- **Missing folder descriptors:** Every folder needs `<folder-name>.md`.
- **Orphaned files:** Files that don't fit the theme of their parent folder.

**Guided mode: STOP here.** Wait for the user's response before proceeding.

### Phase 2: Content freshness

Use git log and git diff to find recent project changes, then check whether
context-db reflects them. For each document, verify that referenced files,
functions, patterns, and tools still exist and haven't been renamed or removed.

Fix clearly outdated content directly. For ambiguous staleness, describe what
looks off and ask.

**Guided mode: STOP here.** Wait for the user's response before proceeding.

### Phase 3: Coverage gaps

Scan all project sources — markdown docs, READMEs, code, config, CI/CD, and
recent git additions — for important topics context-db doesn't cover. Look for
gotchas, design rationale, and cross-cutting concerns that an agent couldn't
infer from any single file.

Describe each gap and ask the user whether to create a new entry.

**Guided mode: STOP here.** Wait for the user's response before proceeding.

### Phase 4: Documentation drift

Compare context-db against documentation sources found in Phase 3. Where they
disagree, check the code to determine which is correct. Report discrepancies
with your assessment. Do not modify files outside context-db without explicit
permission.

**Guided mode: STOP here.** Wait for the user's response before proceeding.

### Phase 5: Content value — is this earning its tokens?

The most common context-db failure is **restating what the code already says**.
Every line of context-db costs tokens to read. Verbose context-db is worse than
no context-db — an agent wastes turns reading summaries when it could read the
source directly in less time.

For each document, ask: "Could an agent figure this out by reading the code?"

**Delete or rewrite** content that falls into these categories:

- **Code summaries.** "The Shape base class has `x`, `y`, `width`, `height`
  properties." → The agent reads `base.py` in one turn and gets more detail.
- **Module layouts.** ASCII tree diagrams of the source directory. → `ls` is
  faster and always current.
- **Property lists and API signatures.** → These belong in docstrings.
- **Step-by-step explanations of how a function works.** → The agent reads the
  function.

**Keep and strengthen** content in these categories:

- **Gotchas.** "Custom constructor params must be set BEFORE
  `super().__init__()` because super calls `draw()`." → You can't learn this
  from reading `draw()` alone. It only bites you when you subclass.
- **Cross-file checklists.** "Adding a new shape? 1. Create class in
  `shapes/`. 2. Add renderer to SVG backend. 3. Add isinstance dispatch. 4.
  Export from `__init__.py`." → Each file makes sense on its own, but knowing
  _which files must change together_ is the hard part.
- **Why, not what.** "SVG backend draws fill and stroke as separate elements
  because SVG strokes are centered on the boundary, causing alpha compositing
  artifacts with semi-transparent fills." → The code shows the separation; only
  context-db explains why it exists.
- **Architecture at the highest level.** One paragraph on how major pieces
  connect. Not a module-by-module walkthrough.

A good test: if you removed a document entirely, would the agent make a mistake
it wouldn't otherwise make? If not, the document isn't earning its tokens.

**Guided mode: STOP here.** Wait for the user's response before proceeding.

### Phase 6: Cross-references

Check "See also" links at the bottom of document bodies. Cross-references can
point to anything in the project — other context-db docs, source code, docs
pages, config files.

- **Broken links.** Fix references to files that no longer exist.
- **Missing links.** Suggest cross-references where an agent would genuinely
  benefit from a pointer to related code, docs, or context-db documents. Don't
  add links just to have them.

**Guided mode: STOP here.** Wait for the user's response before proceeding.

### Phase 7: Reindex

Read `templates/skills/context-db-reindex/SKILL.md` and follow its steps to
reindex all descriptions in the target path. This ensures descriptions reflect
all content changes made during the audit.

## Interaction style

**Be chatty.** This is a collaborative review, not a silent batch job. Explain
your reasoning as you work through each phase. Summarize findings at the end of
each phase before moving to the next.

**Ask before acting** on anything ambiguous — reorganizing folders, creating new
entries, removing content, resolving disagreements between sources.

**Act without asking** when something is clearly wrong — a description that says
"Overview" for a file about auth tokens, a reference to a file that no longer
exists, a folder with 15 items that obviously needs splitting.

**If something is fine, say so and move on.** Don't rewrite things that are
already good. The audit should report what it found, not change things for the
sake of changing them.

## Verify

After all changes, run the TOC script on affected folders to confirm the output:

```
.claude/skills/context-db-manual/scripts/context-db-generate-toc.sh <folder>
```
