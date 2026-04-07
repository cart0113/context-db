# context-db

A portable standard for organizing project knowledge as Markdown files. Inspired
by the `SKILLS.md` standard, documents and folders contain YAML frontmatter with
brief content summaries. Then, through AGENTS.md files, skills, rules, or other
instructions, agents are pointed to a `context-db-instructions.md` file and can:

- Learn how to use the `bin/show_toc.sh` bash script to dynamically auto
  generate folder table of contents to support progressive discovery.
- Learn how to maintain the context-db knowledge database so context and
  knowledge can be built up over time.

The goal of context-db was to create a lighter weight system than the
`SKILLS.md` system that is:

- _Hierarchical_. By organizing content into nested folders and files, the
  system further supports progressive disclosure as an agent reads in the tables
  of contents of one folder at a time.
- _Lightweight_. context-db folders and files are just context/knowledge md
  files with summaries. For project context, structure, and knowledge this is
  often a more natural fit and you do not need all the additional features that
  skills provide (service script, etc.).

Overall, trying to fit all project context/knowledge into skills is often an
awkward fit and the wiki/book format of context-db is a more natural choice.

## Folder structure

```
your-project/
├── AGENTS.md                          ← tells agent -> read context-db-instructions.md
├── bin/show_toc.sh                    ← dynamic TOC generator
└── context-db/
    ├── context-db-instructions.md     ← reading/writing rules
    ├── <project-name>-project/        ← main project context
    │   ├── <project-name>-project.md  ← folder description (frontmatter only)
    │   ├── architecture.md            ← document (frontmatter + body)
    │   └── data-model/
    │       ├── data-model.md
    │       └── entities.md
    ├── coding-standards/              ← ancillary (symlinked from another repo)
    │   ├── coding-standards.md
    │   ├── general-coding-standards.md
    │   ├── python-coding-standards.md
    │   └── javascript-coding-standards.md
    └── writing-standards/             ← ancillary (symlinked from another repo)
        ├── writing-standards.md
        └── first-person-voice.md
```

## How It Works

1. Copy the `context-db/context-db-instructions.md` and `bin/show_toc.sh` into
   your project (both are in `templates/`).
2. Set up an `AGENTS.md`, skill, rule, or some way to point an agent to the
   `context-db/context-db-instructions.md`.
3. Build up your context-db knowledge database over time.
4. The agent runs `bin/show_toc.sh context-db/` to start the progressive
   browsing of the knowledge database.
5. Descriptions in YAML frontmatter let the agent skip irrelevant branches.
6. When the agent learns something important, it writes it back to context-db.

## Structure

```
templates/              Copy these into your project
  bin/show_toc.sh       TOC generator
  context-db/           Instructions file
  AGENTS.md             Sample agent config section
  skills/context-db/    Sample SKILLS.md for Claude Code
bin/show_toc.sh         Canonical TOC generator
context-db/             This project's own knowledge database
example/                Example project structure
docs/                   GitHub Pages documentation
```

## Documentation

Full docs: https://cart0113.github.io/context-db/

## License

MIT
