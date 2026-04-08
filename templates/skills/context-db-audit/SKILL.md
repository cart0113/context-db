---
name: context-db-audit
description: >-
  Audit context-db against project code, docs, and git history — find stale
  entries, missing topics, structural problems, and doc/context-db drift.
  TRIGGER when: user asks to review or audit the knowledge base, or after major
  project changes.
argument-hint: '[folder-path]'
allowed-tools: Read Write Edit Glob Grep Bash
---

## What this does

Perform a thorough audit of the context-db knowledge base by cross-referencing
it against the actual project — code, docs, git history, and any other sources
of truth. Identify problems and fix or flag them.

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
.claude/skills/context-db-audit/scripts/context-db-list-files.sh <target-path>
```

## Audience

The primary audience for context-db is LLM agents, though it should be useful
for humans too. Every description and every document must help an agentic system
get up to speed on the project using the smallest context window possible. Every
word costs tokens. When evaluating content freshness, coverage gaps, and
description quality, judge everything through this lens — include what an agent
cannot infer from the code, omit what it can.

## Audit phases

Work through these phases in order. Be conversational — explain what you're
finding as you go. Ask the user for input on anything that isn't clearly wrong.

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

### Phase 3: Coverage gaps

Scan the project for important topics that context-db doesn't cover:

1. **Code patterns** — look at the project structure, key directories, and
   important files. Are there major subsystems or conventions not documented?
2. **Documentation directories** — find `docs/`, `README.md`, and any other
   documentation sources. Compare their content against context-db.
3. **Configuration** — check for non-obvious config files, CI/CD setup, deploy
   scripts, or infrastructure that would be useful context.
4. **Recent additions** — use git log to find recently added files or
   directories that may need context-db entries.

For each gap found, describe what's missing and ask the user whether to create a
new entry. Do not create entries without asking — the user knows what's
important.

### Phase 4: Documentation drift

Compare context-db against other documentation sources in the project (`docs/`,
README files, wiki references, etc.):

- If context-db and docs **agree**, no action needed.
- If context-db and docs **disagree**, determine which is more likely correct by
  checking the code. Report the discrepancy with your assessment.
- If context-db is correct but docs are stale, point this out — the user may
  want to update the docs to match. Do not modify files outside context-db
  without explicit permission.
- If docs are correct but context-db is stale, propose the update and ask before
  making changes.

### Phase 5: Description quality

After content and structure are resolved, do a quick pass on all descriptions:

- Are they concise but complete enough for an agent to judge relevance?
- Do they front-load the key concept?
- Are any just titles or filler?

For clearly bad descriptions, fix them and tell the user. For borderline cases,
propose alternatives and ask.

## Interaction style

**Be chatty.** This is a collaborative review, not a silent batch job. Explain
your reasoning as you work through each phase. Summarize findings at the end of
each phase before moving to the next.

**Ask before acting** on anything ambiguous — reorganizing folders, creating new
entries, removing content, resolving disagreements between sources.

**Act without asking** when something is clearly wrong — a description that says
"Overview" for a file about auth tokens, a reference to a file that no longer
exists, a folder with 15 items that obviously needs splitting.

**Point out wins too.** If a section is well-organized or a description is
particularly good, say so. The audit isn't just about finding problems.

## Verify

After all changes, run the TOC script on affected folders to confirm the output:

```
.claude/skills/context-db-manual/scripts/context-db-generate-toc.sh <folder>
```
