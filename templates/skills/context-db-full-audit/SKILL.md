---
name: context-db-full-audit
description: >-
  Full audit — reindex all descriptions, then audit against project code, docs,
  and git history for stale entries, missing topics, structural problems,
  cross-references, and doc drift. TRIGGER when: user asks to review or audit
  the knowledge base, or after major project changes.
argument-hint: '[folder-path]'
allowed-tools: Read Write Edit Glob Grep Bash
---

## What this does

Full audit: reindex all descriptions, then audit the knowledge base against
**all** project sources of truth — code, markdown documentation, user-facing
docs, README files, git history, and configuration.

**This skill includes a reindex.** Before starting, read the reindex
instructions at `templates/skills/context-db-reindex/SKILL.md` — that defines
how Phase 0 works.

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
> 1. **Guided** — I report each phase's findings and wait for your input before
>    moving on. You steer what gets fixed.
> 2. **Autonomous** — I run all phases, fix what's clearly wrong, and give you a
>    summary at the end with questions on anything ambiguous.
>
> Which do you prefer?

**Wait for their answer.** Do not proceed until they respond.

- If they choose **Guided**: after each phase, present your findings, then
  **stop and wait** for the user to respond before starting the next phase.
- If they choose **Autonomous**: run all phases back-to-back, fix clear issues,
  and collect ambiguous questions for a single summary at the end.

## Audit phases

Work through these phases in order. Be conversational — explain what you're
finding as you go. Ask the user for input on anything that isn't clearly wrong.

**IMPORTANT — pacing:** In Guided mode, each phase ends with a summary and
questions. You MUST wait for the user's response before starting the next phase.
Do not ask a question and then answer it yourself in the same turn.

### Phase 0: Reindex

Read `templates/skills/context-db-reindex/SKILL.md` and follow its steps to
reindex all descriptions in the target path. This ensures descriptions are
accurate before the audit evaluates them.

**Guided mode: STOP here.** Wait for the user's response before proceeding.

### Phase 1: Structural health

Check the tree structure for violations of logarithmic progressive disclosure.

**The rule:** each folder level should halve the search space. 5–10 items per
folder is the target. Too many items at one level forces agents to scan a long
list instead of navigating a decision tree.

Check for:

- **Too many items:** Any folder with more than 10 children (files + subfolders)
  needs splitting. Propose a reorganization and ask the user before making
  changes.
- **Too few items:** A subfolder with only 1–2 files may not justify its own
  level. Propose merging upward.
- **Depth problems:** More than 3–4 levels deep is a smell. The tree should be
  wide and shallow, not narrow and deep.
- **Missing folder descriptors:** Every folder needs `<folder-name>.md`. Flag
  any that are missing.
- **Orphaned files:** Files that don't fit the theme of their parent folder.

Report findings for this phase and ask the user if they want you to fix
structural issues before continuing.

**Guided mode: STOP here.** Wait for the user's response before proceeding.

### Phase 2: Content freshness

Use git to find what has changed in the project and whether context-db reflects
those changes.

```bash
# If git is available, check recent changes
git log --oneline --since="2 weeks ago" --name-only 2>/dev/null
git diff --name-only HEAD~20 2>/dev/null
```

For each context-db document:

1. Read the document fully.
2. Check whether the topics it covers still match the current state of the code
   or project.
3. Look for references to files, functions, patterns, or tools that may have
   been renamed, removed, or changed.

Flag documents that appear stale. For clearly outdated content (references to
deleted files, removed features, old patterns), fix it directly and tell the
user what you changed. For ambiguous cases, describe what looks off and ask.

**Guided mode: STOP here.** Wait for the user's response before proceeding.

### Phase 3: Coverage gaps

Scan **all** project sources — code, docs, and configuration — for important
topics that context-db doesn't cover. context-db should integrate knowledge from
every source, not just mirror one.

1. **All markdown files** — find every `*.md` file in the project (outside
   `context-db/` itself). README files, `docs/` directories, contributing
   guides, changelogs, ADRs, design docs — read them all. These often contain
   gotchas, design rationale, and setup instructions that belong in context-db.
2. **Code patterns** — look at the project structure, key directories, and
   important files. Are there major subsystems or conventions not documented?
3. **Configuration** — check for non-obvious config files, CI/CD setup, deploy
   scripts, or infrastructure that would be useful context.
4. **Recent additions** — use git log to find recently added files or
   directories that may need context-db entries.

For each gap found, describe what's missing and ask the user whether to create a
new entry. Do not create entries without asking — the user knows what's
important.

**Guided mode: STOP here.** Wait for the user's response before proceeding.

### Phase 4: Documentation drift

Compare context-db against **every** documentation source discovered in Phase 3
(all `*.md` files, `docs/` directories, README files, wiki references, etc.):

- If context-db and docs **agree**, no action needed.
- If context-db and docs **disagree**, determine which is more likely correct by
  checking the code. Report the discrepancy with your assessment.
- If context-db is correct but docs are stale, point this out — the user may
  want to update the docs to match. Do not modify files outside context-db
  without explicit permission.
- If docs are correct but context-db is stale, propose the update and ask before
  making changes.

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

### Phase 6: Description quality

After content is resolved, do a quick pass on all descriptions:

- Are they concise but complete enough for an agent to judge relevance?
- Do they front-load the key concept?
- Are any just titles or filler?

For clearly bad descriptions, fix them and tell the user. For borderline cases,
propose alternatives and ask.

**Guided mode: STOP here.** Wait for the user's response before proceeding.

### Phase 7: Cross-references

Check "See also" links at the bottom of document bodies.

- **Broken links.** Fix references to files that no longer exist.
- **Missing links.** Look for documents in different folders that cover related
  topics but don't reference each other. Suggest cross-references where an agent
  navigating one branch would genuinely benefit from knowing about a document in
  another branch. Don't add links just to have them.

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
