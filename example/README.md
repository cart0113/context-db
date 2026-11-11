# Example: acme-payments-repo

A small project that uses context-db, ready to run.

```
example/
├── shared/                             standards that "another repository" owns
│   ├── coding-standards/
│   └── git-standards/
└── acme-payments-repo/                 the example project
    ├── AGENTS.md
    ├── .claude/skills/context-db       symlink to ../../skill/context-db
    └── context-db/
        ├── configuration/              settings.md; ON_PROMPT.md carries a PCI reminder
        ├── acme-payments-project/      the project folder
        │   ├── architecture.md
        │   ├── api-reference.md
        │   ├── data-model/
        │   └── wip/                    wip.md lists refund-endpoint.md
        ├── coding-standards -> ../../shared/coding-standards
        └── git-standards -> ../../shared/git-standards
```

Try it:

```bash
cd example/acme-payments-repo
python3 .claude/skills/context-db/context-db.py prompt "add a refund endpoint"
python3 .claude/skills/context-db/context-db.py wip --list
python3 .claude/skills/context-db/context-db.py toc
python3 .claude/skills/context-db/context-db.py toc context-db/coding-standards
python3 .claude/skills/context-db/context-db.py toc --check
```
