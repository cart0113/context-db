# Example: acme-payments-repo

A runnable reference layout.

```
example/
├── shared/                             standards owned by "another repo"
│   ├── coding-standards/
│   └── git-standards/
└── acme-payments-repo/                 the example project
    ├── AGENTS.md
    ├── .claude/skills/context-db       symlink to ../../skill/context-db
    └── context-db/
        ├── context-db.json
        ├── context-db-on-markdown/     ON_PROMPT.md carries a PCI reminder
        ├── acme-payments-project/      the project bundle
        │   ├── architecture.md
        │   ├── api-reference.md
        │   ├── data-model/
        │   └── wip/refund-endpoint.md
        ├── coding-standards -> ../../shared/coding-standards
        └── git-standards -> ../../shared/git-standards
```

Try it:

```bash
cd example/acme-payments-repo
python3 .claude/skills/context-db/context-db.py prompt "add a refund endpoint"
python3 .claude/skills/context-db/context-db.py wip
python3 .claude/skills/context-db/context-db.py index --check
```

The two symlinked bundles are indexed from the folder that owns them:

```bash
cd example/shared
python3 ../../skill/context-db/context-db.py index coding-standards
```
