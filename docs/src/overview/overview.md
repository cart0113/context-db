# Overview

`context-db` is a portable standard for organizing project knowledge as Markdown
files. Inspired by the `SKILLS.md` standard, documents and folders contain YAML
frontmatter with brief content summaries. Then, through AGENTS.md files, skills,
rules, or other instructions, agents are pointed to a
`context-db-instructions.md` file and can:

- Learn how to use the `bin/show_toc.sh` bash script to dynamically auto
  generate folder table of contents to support progressive discovery.
- Learn how to maintain the `context-db` knowledge database so context and
  knowledge can be built up over time.

The goal of `context-db` was to create a lighter weight system than the
`SKILLS.md` system that is:

- _Hierarchical_. By organizing content into nested folders and files, the
  system further supports progressive disclosure as an agent reads in the tables
  of contents of one folder at a time.
- _Lightweight_. `context-db` folders and files are just context/knowledge md
  files with summaries. For project context, structure, and knowledge this is
  often a more natural fit and you do not need all the additional features that
  skills provide (service script, etc.).

An emerging trend is to use the skills format for ALL project knowledge —
repurposing a system originally designed to teach agents about discrete how-to
behaviors. Often this is an awkward fit and the wiki/book format of `context-db`
is a more natural choice (more like how Obsidian vaults work). Skills are
instructions on how to do something and define discrete tools. `context-db` is
more for free-form, general project knowledge and context.

## Folder structure

A typical layout might look like:

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

Here:

- By convention, the main project folder is called `<project-name>-project/` and
  is the entry point into your main project knowledge files.
- In parallel, you may have other common context you routinely want included
  (coding standards, notes on how to use documentation tools, etc.).
- Every folder must have a `<folder-name>.md` file in it which only contains
  YAML frontmatter with a summary of what is in the folder.

## How It Works

1. Copy the `context-db/context-db-instructions.md` and `bin/show_toc.sh` into
   your project (both are in `templates/`).
2. Set up an `AGENTS.md`, skill, rule, or some way to point an agent to the
   `context-db/context-db-instructions.md`.
3. Build up your `context-db` knowledge database over time.
4. The agent runs `bin/show_toc.sh context-db/` to start the progressive
   browsing of the knowledge database.
5. Descriptions in YAML frontmatter let the agent skip irrelevant branches.
6. When the agent learns something important, it writes it back to `context-db`.
