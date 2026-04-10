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

**First, do no harm.** Context-db gives agents confidence, and confidence
reduces how much code they read. A bad context-db causes mistakes the agent
wouldn't have made without it. The best entries are small, point to the code
rather than summarizing it, and document only what the code can't tell you:
traps, non-obvious connections between files, and design rationale. A 200-line
context-db that points to code outperforms a 1000-line one that summarizes it.

An audit is not just a health check — it's an opportunity to grow the knowledge
base. If the project has areas that aren't covered, add new files, new folders,
new hierarchy as needed. Follow the structural rules (5–10 items per folder, 3–4
levels deep), but don't let the existing structure limit what gets documented.
The structure serves the content, not the other way around.

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

LLM agents first, humans second. Every word costs tokens. Include what an agent
can't infer from the code, omit what it can.

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
- **Missing folder descriptors:** Every subfolder needs `<folder-name>.md`.
  Exception: do not create `context-db/context-db.md` — the root folder does not
  need a descriptor.
- **Orphaned files:** Files that don't fit the theme of their parent folder.
- **Vague descriptions.** Descriptions are routing decisions — an agent reads
  them to decide whether to drill into a folder or file. A description like
  "Architecture overview" or "Project notes" forces the agent to open the file
  to find out if it's relevant. Good descriptions name the specific topics
  covered so the agent can skip irrelevant files without reading them. Check
  every description in the TOC output and flag any that don't give enough signal
  for an agent to make a skip/read decision.

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

**Project map completeness.** Somewhere in the context-db — the project root
descriptor, a dedicated architecture doc, or across subfolder descriptions — an
agent must be able to learn what major subsystems exist, where they live, and
how they connect. This is not a code summary — it's an inventory. `ls` shows
files, not purpose or relationships. Without this map, agents miss entire
subsystems and either explore blind or reimplement things that already exist.

To check completeness: run `ls` on the project's top-level source directories
and packages — actually list them, don't work from memory. For each directory,
ask: "Could an agent reading only the context-db learn that this subsystem
exists and what role it plays?" If not, it's a gap. Don't prescribe where the
information should live — flag the gap and let the user decide the right home
for it.

Describe each gap and ask the user whether to create a new entry.

**Guided mode: STOP here.** Wait for the user's response before proceeding.

### Phase 4: Documentation drift

Compare context-db against documentation sources found in Phase 3. Where they
disagree, check the code to determine which is correct. Report discrepancies
with your assessment. Do not modify files outside context-db without explicit
permission.

**Guided mode: STOP here.** Wait for the user's response before proceeding.

### Phase 5: Content value — is every topic earning its tokens?

Context-db gives agents confidence, and confidence reduces how much code they
read. Every piece of content must justify the confidence it creates. Too verbose
and the agent wastes turns reading summaries. Too thin and it gets no signal.
Too instructional and it follows steps instead of reading code.

**For each document, check three things.**

#### Does it point to code or replace it?

The best content names a reference implementation and documents what's
non-obvious about it. Cut anything the agent could learn faster by reading the
code directly:

- Code summaries, property lists, API signatures → agent reads the source
- Module layouts → `ls` is faster and always current
- Step-by-step instructions → agent reads a reference implementation instead.
  Instructions create blind spots: the agent follows the steps and misses
  anything not listed

#### Does it document what breaks?

The highest-value content documents ripple effects — what else must change when
you modify something in this area, that the agent won't find by tracing the call
chain or grepping for the relevant symbol. Files in other packages. Config
entries referenced by string literal. Schema files that need matching entries.
Things that already exist that the agent might reimplement. Ordering constraints
between subsystems.

If a document describes a change pattern but doesn't mention what else is
affected, it's incomplete.

#### Is it too thin to help?

Read the actual code the topic covers. Ask: "If an agent made a change in this
area with only this document and the code, what would it get wrong?" If you find
traps the document doesn't mention, add them.

**Don't just flag problems — fix them.** Write at the "just right" level from
the calibration examples below.

#### Calibration examples

**Subsystem inventory:**

> Too thin: "The `src/services/` directory contains application services."
>
> Just right: "Services in `src/services/`: loop detection (multi-tier,
> integrated into client loop), execution lifecycle, telemetry, tracker. Check
> here before building new infrastructure."
>
> Too verbose: "`loopDetectionService.ts` exports `LoopDetectionService` with
> methods `checkForLoop(history)`, `getConsecutiveCount()`..."

**Change patterns:**

> Too thin: "Adding a hook requires changes to the types file and handler."
>
> Just right: "Read `BeforeTool` end-to-end before adding a hook event. The core
> hook machinery is discoverable. Non-obvious: settings registration is in a
> different package (`packages/cli/`), and the fire site matters (tool hooks
> fire from `coreToolHookTriggers.ts`, policy hooks from `scheduler.ts`)."
>
> Harmful: "1. Add to enum. 2. Add interfaces. 3. Add fire method..." — agent
> follows steps, stops reading, misses anything not listed.

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
