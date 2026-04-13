## Mission

Build the smallest knowledge base that prevents agents from making mistakes
they'd make with only the code. Every audit decision — what to cut, keep,
rewrite, or rarely add — is measured against: _would an agent get this wrong
after reading the code?_ If not, it doesn't belong.

**First, do no harm.** Content describing code state is actively harmful —
agents trust the description, skip the code, and fail when it drifts. The best
entries document only what the code can't tell you: conventions, pitfalls,
non-obvious connections, and design rationale.

**The default posture is to cut.** An audit should leave context-db smaller and
sharper, not larger.

## Target

{target_path}

## External symlinks — do NOT follow

context-db folders often contain symlinks to shared standards from other repos.
**Never follow, read, edit, or audit files that resolve outside this project.**
Use the TOC script to discover files — it shows only project-local content:

```
python3 {toc} {target_path}
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
user's response after each phase.

### Phase 1: Structural health

Enforce B-tree structure. Target: 5-10 items per folder, 50-150 lines per file,
reachable in 2-3 navigation steps.

- **>10 children:** Split into subfolders.
- **1-2 files:** Merge upward into parent folder.
- **>3-4 levels deep:** Flatten. Wide and shallow beats narrow and deep.
- **>200 lines:** Split into a subfolder with the same name.
- **Missing folder descriptors:** Every subfolder needs `<folder-name>.md`.
- **Vague descriptions:** Descriptions are routing decisions. Good descriptions
  name specific topics so the agent can skip without reading.

### Phase 2: Content freshness

Use git log and git diff to find recent project changes, then verify that
referenced files, functions, and patterns still exist. Fix clearly outdated
content directly.

### Phase 3: Content value — is every topic earning its tokens?

Cut anything the agent could learn faster by reading code:

- Code summaries, property lists, API signatures
- Module layouts
- Step-by-step instructions

The highest-value content documents ripple effects — what else must change that
the agent won't find by tracing the call chain.

### Phase 4: Coverage gaps

Look for genuine pitfalls — non-obvious constraints and cross-cutting concerns
agents can't infer from code alone. Check recent git history for corrections and
reverts.

### Phase 5: Documentation drift

Compare context-db against project documentation. Where they disagree, check the
code to determine which is correct.

### Phase 6: Cross-references

Check "See also" links. Fix broken references. Suggest new cross-references only
where genuinely helpful.

### Phase 7: Reindex

Re-read every file in the target path and update all `description` fields in
YAML frontmatter so they accurately reflect current content.

Steps:

1. Ensure every subfolder has `<folder-name>.md` (except root `context-db/`)
2. For each .md file: read content, evaluate description accuracy, rewrite if
   needed
3. Reindex folder descriptors bottom-up (deepest first)
4. Run the TOC script on every folder to verify:

```
python3 {toc} {target_path}
```

Fix any YAML frontmatter issues found.

## Verify

After all changes, run the TOC script on every folder and subfolder to catch
problems:

```
python3 {toc} {target_path}
```
