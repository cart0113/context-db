---
name: context-db-reindex
description: >-
  Reindex context-db — re-read every file, rewrite all descriptions to match
  current content, and create missing folder description files. TRIGGER when:
  context-db files have been edited and descriptions may be stale, or after bulk
  changes to the knowledge base.
argument-hint: '[folder-path]'
allowed-tools: Read Write Edit Glob Grep Bash
---

## What this does

Re-read every file in context-db and update all `description` fields in
frontmatter so they accurately reflect current content. Also ensure every folder
has its `<folder-name>.md` descriptor file, creating any that are missing.

## Target

If `$ARGUMENTS` is provided, treat it as the root folder to reindex (e.g.
`context-db/coding-standards/`). Reindex that folder and all subfolders
recursively.

If no argument is provided, reindex the entire `context-db/` directory.

## Audience

The primary audience for context-db is LLM agents, though it should be useful
for humans too. Every description and every document you write must help an
agentic system get up to speed on the project using the smallest context window
possible. Every word costs tokens. Write for maximum signal density — include
what an agent cannot infer from the code, omit what it can.

## External symlinks — do NOT follow

context-db folders often contain symlinks to shared standards from other repos.
**Never follow, read, edit, or reindex files that resolve outside this
project.** They are owned by another repo and must not be modified here.
Symlinks that resolve within this project are fine.

Use the listing script (not Glob) to discover files — it filters out external
symlinks automatically:

```
.claude/skills/context-db-reindex/scripts/context-db-list-files.sh <target-path>
```

## Steps

### 1. Discover all folders and files

Run the listing script on the target path. Build a map of:

- Every folder that contains `.md` files
- Every `.md` file and its current `description` frontmatter

### 2. Ensure folder descriptors exist

For every folder, check whether `<folder-name>.md` exists inside that folder
(e.g. `coding-standards/coding-standards.md`). If it does not exist:

1. Read all files in the folder to understand its contents.
2. Write a new `<folder-name>.md` with frontmatter only — no body content:

```yaml
---
description: <concise summary of what this folder contains>
---
```

### 3. Reindex every file

For each `.md` file (including newly created folder descriptors):

1. Read the full file content.
2. Evaluate whether the current `description` accurately and completely
   summarizes what the file contains.
3. If the description is missing, inaccurate, incomplete, or could be improved —
   rewrite it using the Edit tool.

### 4. Reindex folder descriptors based on children

After all files are updated, revisit each `<folder-name>.md`:

1. Read the now-updated descriptions of all children (files and subfolder
   descriptors) in that folder.
2. Rewrite the folder's `description` to accurately summarize the collection of
   children.
3. Work bottom-up — do deepest folders first so parent descriptions reflect
   updated child descriptions.

### 5. Verify

Run the TOC script on each affected folder to confirm the output looks correct:

```
.claude/skills/context-db-manual/scripts/context-db-generate-toc.sh <folder>
```

## How to write descriptions

Descriptions are the primary way agents decide whether to read a file.

**Be concise but complete.** Include all detail an agent would need to decide
whether to open the file — but no more. Every word must earn its place.

**Summarize content, not titles.** A description like "Overview of the auth
system" is a title. A description like "How auth tokens are issued, validated,
and refreshed — covers JWT structure, session lifecycle, and token rotation
policy" tells the agent exactly what's inside.

**Front-load the key concept.** Agents scan descriptions quickly. Put the most
important keyword or concept first.

**Bad examples:**

- `Overview` — says nothing
- `Standards for coding` — too vague to decide relevance
- `This file contains information about...` — filler

**Good examples:**

- `How auth tokens are issued, validated, and refreshed — JWT structure, session lifecycle, token rotation`
- `Python-specific standards — naming, imports, type hints, virtual environments`
- `Reindex context-db — re-read every file, rewrite all descriptions to match current content`

## Handling ambiguity

This skill is mostly automated — update descriptions without asking unless you
are genuinely unsure what a file is about. Specific cases where you should ask:

- A file's content seems contradictory or outdated and you can't tell which
  parts are current
- A file has no clear purpose and you're unsure whether it should exist
- A folder's contents don't form a coherent group and you're unsure how to
  summarize them

In those cases, use AskUserQuestion to clarify before writing.
