---
name: context-db-manual
description:
  'How to use context-db — load this skill fully on startup. Markdown knowledge
  base containing project context, conventions, design decisions, cross-file
  connections, common pitfalls, etc.'
allowed-tools: Bash Read
---

`context-db/` is this project's knowledge base. It documents architecture,
gotchas, design decisions, and cross-file connections — things you can't learn
from reading any single file. It does not contain everything — it's a starting
point, a map, a hint — but it helps you orient yourself in a project quickly.

**Context files describing information an agent can determine by using `find`,
`grep`, and `read` can be harmful to agent performance.** Only document what the
code can't tell you.

## Reading

Browse what's available with the TOC script:

```
.claude/skills/context-db-manual/scripts/context-db-generate-toc.sh context-db/
```

Every file and folder has a `description` in its YAML frontmatter. The TOC
script lists descriptions for every file and subfolder in a folder. Use them to
decide what to read and what to skip — drill into relevant topics, ignore the
rest. Context-db is a B-tree: agents read descriptions at each level and branch
into the relevant folder, narrowing by 5–10x per level. Any topic should be
reachable in 2–3 navigation steps.

## Updating

After completing a task, update context-db only if you encountered something
that would mislead the next agent — a non-obvious dependency, a constraint
invisible in the code, a convention the agent wouldn't know, or a correction
from the user. Do not summarize what the code does; the next agent reads the
code.

Update existing files when they cover the topic. Create new files only for
genuinely new pitfalls or conventions. Delete content that has drifted into code
summary. A smaller, accurate context-db outperforms a larger, comprehensive one.

Every `.md` file needs YAML frontmatter with a `description` field — this is the
routing decision agents use to decide whether to open the file. Be specific:
"scheduler execution flow, budget enforcement hook" not "Architecture overview."
Two types: documents (frontmatter + body) and folder descriptors (frontmatter
only, named `<folder-name>.md`). Every subfolder needs a folder descriptor — it
summarizes what the folder contains so agents can decide whether to drill in.
The root `context-db/` folder does not get one; it is never read.

Structure: 5–10 items per folder, target 50–150 lines per file, 200 max. If a
file exceeds 200 lines, split it into a subfolder with the same name — the file
becomes the folder descriptor and content splits into smaller files. After
changes, run the TOC script to verify.

## What belongs

_"Would removing this cause the next agent to make a mistake, even after reading
the code?"_ If not, leave it out.

- **Conventions.** How this project does things — naming, patterns, structure,
  tooling choices. Without these, agents default to their training and produce
  code that works but doesn't match the project.
- **Corrections.** Corrections to an agent mid-task, or instructions you find
  yourself repeating — proven knowledge the agent couldn't derive from code.
- **Pitfalls.** Ripple effects, files that must change together but aren't
  linked by imports, non-obvious ordering constraints, silent failures.
- **Rationale.** Design decisions invisible in the code — constraints,
  trade-offs, choices that would look wrong without context.
- **Domain knowledge.** Protocols or concepts specific to this project's domain
  that models weren't trained on.

## What does NOT belong

Every token of context-db displaces a token of code the agent could read. When
in doubt, leave it out.

- **Code state** — what exists, what it does, how it's structured. These
  descriptions drift, and agents trusting stale descriptions make worse mistakes
  than agents reading code fresh.
- **Step-by-step instructions** — agents follow the steps, stop reading, and
  miss anything not listed. Point to a reference implementation instead.
- **Anything derivable in 30 seconds** — if `ls`, `grep`, or reading one file
  would reveal it, it doesn't belong.
