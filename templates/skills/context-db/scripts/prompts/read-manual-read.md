## Reading context-db

`{context_db_rel}/` is this project's knowledge base. It documents architecture,
gotchas, design decisions, conventions, and cross-file connections — things you
can't learn from reading any single file. It does not contain everything — it's
a starting point, a map, a hint — but it helps you orient yourself quickly.

**Context files describing information an agent can determine by using `find`,
`grep`, and `read` can be harmful to agent performance.** Only what the code
can't tell you is documented.

### How to navigate

Browse what's available with the TOC script:

```
python3 {toc} {context_db_rel}/
```

Every file and folder has a `description` in its YAML frontmatter. The TOC
script lists descriptions for every file and subfolder. Use them to decide what
to read and what to skip — drill into relevant topics, ignore the rest.

Context-db is a B-tree: read descriptions at each level and branch into the
relevant folder, narrowing by 5-10x per level. Any topic should be reachable in
2-3 navigation steps.

### What belongs in context-db

_"Would removing this cause the next agent to make a mistake, even after reading
the code?"_ If not, leave it out.

- **Conventions.** How this project does things — naming, patterns, structure.
- **Corrections.** Corrections to an agent mid-task, or instructions you find
  yourself repeating.
- **Pitfalls.** Ripple effects, files that must change together but aren't
  linked by imports, non-obvious ordering constraints.
- **Rationale.** Design decisions invisible in the code.
- **Domain knowledge.** Protocols or concepts specific to this project's domain.

### What does NOT belong

- **Code state** — what exists, what it does, how it's structured. Descriptions
  drift, and agents trusting stale descriptions make worse mistakes.
- **Step-by-step instructions** — agents follow the steps, stop reading, and
  miss anything not listed.
- **Anything derivable in 30 seconds** — if `ls`, `grep`, or reading one file
  would reveal it, it doesn't belong.
