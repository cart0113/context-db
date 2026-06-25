# Example: acme-payments-repo

A runnable reference layout for context-db.

```
example/
├── shared/                          ← cross-project standards
│   ├── coding-standards/
│   └── git-standards/
└── acme-payments-repo/              ← the example project
    ├── AGENTS.md                    ← opt-in standing instructions
    ├── .claude/
    │   └── skills/context-db/       ← scripts symlink to ../templates/...
    └── context-db/
        ├── ON_PROMPT.md             ← inlined on every prompt
        ├── acme-payments-project/
        │   ├── architecture.md
        │   ├── api-reference.md
        │   └── data-model/
        ├── coding-standards -> ../../shared/coding-standards
        └── git-standards -> ../../shared/git-standards
```

The `coding-standards/` and `git-standards/` symlinks demonstrate the
cross-project sharing pattern — a single source of truth lives under
`example/shared/`, and the project's `context-db/` reaches into it.

The dispatcher scripts under `.claude/skills/context-db/scripts/` are symlinked
back to `templates/skills/context-db/scripts/`, so the layout is genuinely
runnable without copying scripts.

## Run the dispatcher against this fixture

```bash
cd example/acme-payments-repo
python3 .claude/skills/context-db/scripts/context-db-main-agent.py prompt "How do I add a new payment endpoint?"
```

Output is what a calling agent would see when the user invokes
`/context-db prompt "..."` — the read mechanics, the context-usage framing, the
`ON_PROMPT.md` content, and the instruction.
