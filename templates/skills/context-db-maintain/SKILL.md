---
name: context-db-maintain
description: >-
  Maintain context-db — cut stale, low-value, or harmful content, fix structural
  problems and doc drift, then reindex. TRIGGER when: user asks to maintain,
  review, or audit the knowledge base, or after major project changes.
argument-hint: '[folder-path]'
allowed-tools: Read Write Edit Glob Grep Bash
---

## Mission

Build the smallest knowledge base that prevents agents from making mistakes
they'd make with only the code. Every audit decision — what to cut, keep,
rewrite, or rarely add — is measured against: _would an agent get this wrong
after reading the code?_ If not, it doesn't belong.

**First, do no harm.** Context-db gives agents confidence, and confidence
reduces how much code they read. Content describing code state is actively
harmful — agents trust the description, skip the code, and fail when it drifts.
The best entries document only what the code can't tell you: conventions,
pitfalls, non-obvious connections, and design rationale. A 200-line context-db
that points to code outperforms a 1000-line one that summarizes it.

**The default posture is to cut.** An audit should leave context-db smaller and
sharper, not larger. Add new content only when you find a genuine pitfall agents
can't derive from code — and even then, keep it minimal.

Write for LLM agents first, humans second. Every word costs tokens.

## Target

If `$ARGUMENTS` is provided, audit that folder and its subfolders. Otherwise
audit the entire `context-db/` directory.

## External symlinks — do NOT follow

context-db folders often contain symlinks to shared standards from other repos.
**Never follow, read, edit, or audit files that resolve outside this project.**
Use the listing script (not Glob) to discover files — it filters out external
symlinks automatically:

```
.claude/skills/context-db-maintain/scripts/context-db-list-files.sh <target-path>
```

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

## Audit phases

Work through these phases in order. In Guided mode, **stop and wait** for the
user's response after each phase. Do not ask a question and then answer it
yourself in the same turn.

### Phase 1: Structural health

Enforce B-tree structure. Target: 5–10 items per folder, 50–150 lines per file,
reachable in 2–3 navigation steps.

- **>10 children:** Split into subfolders. Propose and ask before restructuring.
- **1–2 files:** Merge upward into parent folder.
- **>3–4 levels deep:** Flatten. Wide and shallow beats narrow and deep.
- **>200 lines:** Split into a subfolder with the same name — the file becomes
  the folder descriptor, content splits into smaller files.
- **Missing folder descriptors:** Every subfolder needs `<folder-name>.md`.
- **Delete `context-db/context-db.md` if it exists** — root needs no descriptor.
- **Orphaned files:** Files that don't fit the theme of their parent folder.
- **Vague descriptions:** Descriptions are routing decisions. "Architecture
  overview" forces the agent to open the file. Good descriptions name specific
  topics so the agent can skip without reading.

**Guided mode: STOP here.**

### Phase 2: Content freshness

Use git log and git diff to find recent project changes, then verify that
referenced files, functions, and patterns still exist. Fix clearly outdated
content directly. For ambiguous staleness, describe what looks off and ask.

**Guided mode: STOP here.**

### Phase 3: Content value — is every topic earning its tokens?

Content describing information an agent can determine by using `find`, `grep`,
and `read` is actively harmful — agents trust it, skip the code, and fail when
it drifts. For each document, check three things.

#### Does it point to code or replace it?

Cut anything the agent could learn faster by reading code:

- Code summaries, property lists, API signatures → agent reads the source
- Module layouts → `ls` is faster and always current
- Step-by-step instructions → agent reads a reference implementation instead;
  instructions create blind spots

#### Does it document what breaks?

The highest-value content documents ripple effects — what else must change that
the agent won't find by tracing the call chain. Files in other packages, config
entries referenced by string literal, ordering constraints between subsystems.

#### Is it too thin to help?

Ask: "If an agent changed code in this area with only this document and the
source, what would it get wrong?" If you find pitfalls it doesn't mention, add
them.

**Don't just flag problems — fix them.** Write at the "just right" level:

> **Too thin:** "Adding a hook requires changes to the types file and handler."
>
> **Just right:** "Read `BeforeTool` end-to-end before adding a hook event. The
> core hook machinery is discoverable. Non-obvious: settings registration is in
> a different package (`packages/cli/`), and the fire site matters (tool hooks
> fire from `coreToolHookTriggers.ts`, policy hooks from `scheduler.ts`)."
>
> **Harmful:** "1. Add to enum. 2. Add interfaces. 3. Add fire method..." —
> agent follows steps, stops reading, misses anything not listed.

**Guided mode: STOP here.**

### Phase 4: Coverage gaps

Look for genuine pitfalls — non-obvious constraints and cross-cutting concerns
agents can't infer from code alone. Check recent git history for corrections,
reverts, and bug fixes that suggest recurring problems context-db doesn't cover.

**Be conservative about adding.** Only flag a gap when you can point to a
specific mistake an agent would make without the knowledge. "An agent might not
know X exists" is not a gap. "An agent will try Y and break Z because nothing
links them" is a gap.

**Guided mode: STOP here.**

### Phase 5: Documentation drift

Compare context-db against project documentation. Where they disagree, check the
code to determine which is correct. Report discrepancies. Do not modify files
outside context-db without explicit permission.

**Guided mode: STOP here.**

### Phase 6: Cross-references

Check "See also" links. Fix broken references. Suggest new cross-references only
where an agent would genuinely benefit from the pointer.

**Guided mode: STOP here.**

### Phase 7: Reindex

Read `templates/skills/context-db-reindex/SKILL.md` and follow its steps to
reindex all descriptions in the target path.

## Interaction style

Be conversational — explain your reasoning as you go. Ask before acting on
anything ambiguous. Act without asking when something is clearly wrong. If
something is fine, say so and move on — don't rewrite things that already work.

## Verify

After all changes, run the TOC script on every folder and subfolder to catch
YAML frontmatter problems:

```
.claude/skills/context-db-manual/scripts/context-db-generate-toc.sh context-db/
```

Fix any issues found.
