# context-db

A minimal standard for organizing project knowledge as hierarchical Markdown so
LLM agents can discover and fetch only what they need.

Large `CLAUDE.md` and `AGENTS.md` files loaded every session hurt agent
performance — but agents still need project-specific knowledge for best results.
Mimicking the SKILL.md frontmatter indexing system, context-db gives every file
and folder a YAML `description` field. However, files are organized in folders
and subfolders, and a small bash script mimics vendor skills support and
dynamically generates a table of contents for any folder — creating a
filesystem-based discovery tree with logarithmic progressive disclosure. Agents
navigate to what they need and can skip the rest.

## Why context-db

- **Hierarchical.** Filesystem as a B-tree. Agents read frontmatter descriptions
  at each level and branch into what's relevant, skipping everything else.
- **Logarithmic cost.** 5–10 items per folder, ~100 lines per file. The amount
  read scales with the task, not the total knowledge base.
- **Minimal.** Contains what agents can't derive from code — conventions,
  pitfalls, rationale, domain knowledge. Of course, this is by convention —
  context-db will contain whatever is put in it — but installed instructions
  provided by this project enforce these standards when agents generate the
  content, and the `/context-db-maintain` skill actively prunes content using
  this guidance.

## Folder Structure

```
your-project/
├── .claude/
│   ├── hooks/
│   │   └── session-start-context-db.sh    ← hook: ensures skill loads every session
│   ├── rules/context-db.md                ← rule: load the skill every conversation
│   ├── settings.local.json                ← wires up the SessionStart hook
│   └── skills/
│       ├── context-db-manual/             ← skill: instructions + TOC script
│       │   ├── SKILL.md
│       │   └── scripts/context-db-generate-toc.sh
│       ├── context-db-reindex/            ← skill: reindex descriptions
│       │   └── SKILL.md
│       └── context-db-maintain/           ← skill: maintain (cut, fix, reindex)
│           └── SKILL.md
└── context-db/
    ├── <project-name>-project/            ← project-specific knowledge
    │   ├── <project-name>-project.md      ← folder description (frontmatter only)
    │   ├── project-coding-standards.md     ← project-specific conventions
    │   ├── architecture.md                ← document (frontmatter + body)
    │   └── data-model/
    │       ├── data-model.md
    │       └── entities.md
    ├── coding-standards/                  ← project-agnostic (often symlinked)
    └── writing-standards/                 ← project-agnostic (often symlinked)
```

The `<project-name>-project/` folder holds all knowledge specific to this
project — architecture, data models, domain context, design decisions. Folders
parallel to it (like `coding-standards/`, `writing-standards/`) are
project-agnostic and are often symlinked from a personal or team standards repo
so the same knowledge can be shared across every project that uses context-db.

Every folder has a `<folder-name>.md` file containing only YAML frontmatter —
this is the folder's description shown in the TOC.

## Wiring It In

An agent needs a minimal instruction set to use context-db — how to run the TOC
script, when to read vs skip, and what to update. This is packaged as a
**skill** (`.claude/skills/context-db-manual/`), which conveniently bundles the
TOC script in its `scripts/` directory. When loaded, the agent gets everything
it needs.

Skill preloading mechanisms alone aren't always reliable enough to ensure the
agent reads the instructions on startup. Two stronger options:

A **rule** (`.claude/rules/context-db.md`) tells the agent to load the skill at
the start of every conversation. Rules fire automatically — no user action
needed.

A **SessionStart hook** (`templates/hooks/session-start-context-db.sh`) is even
stronger — it injects the instruction into the conversation context before the
first turn, ensuring the agent reads it every time.

Any mechanism that gets the SKILL.md content in front of the agent works.
Alternative approaches:

- **`AGENTS.md` or `CLAUDE.md`** — paste the SKILL.md content (or a summary)
  directly. Works with any agent framework.
- **Rule with inline instructions** — put the SKILL.md content into a rule file
  instead of referencing the skill. Simpler, but loads the full text every
  conversation.
- **Just the script** — place `context-db-generate-toc.sh` somewhere accessible
  (e.g. `bin/`) and tell the agent where it is and how to use it via whatever
  instruction mechanism is available.

## Getting Started

1. Copy `templates/skills/context-db-manual/` into
   `.claude/skills/context-db-manual/` (or symlink it).
2. Copy `templates/rules/context-db.md` into `.claude/rules/context-db.md` (or
   symlink it).
3. Copy `templates/hooks/session-start-context-db.sh` into `.claude/hooks/` and
   wire it up in `.claude/settings.local.json` (see Wiring It In above).
4. Create `context-db/` in your project and start adding knowledge.

## Private or Public

The TOC script runs dynamically — anything it finds at runtime appears in the
agent's navigation, whether committed, gitignored, or symlinked.

```
context-db/
├── acme-project/                     ← committed, shared with team
├── my-notes/                         ← gitignored, local only
├── personal-coding-standards/        ← symlink, gitignored (personal repo)
└── team-coding-standards/            ← symlink, committed (shared location)
```

Gitignored symlinks can point anywhere. Committed symlinks need to resolve for
all team members — a shared filesystem location or relative path. See
[Cross-Project Sharing](guide/cross-project-sharing.md) for patterns.

## The context problem

> ["To alcohol! The cause of, and solution to, all of life's problems."](https://www.youtube.com/watch?v=SXyrYMxa-VI)
> — Homer Simpson

Similar to Homer's alcohol paradox, context files are both the cause of, and
solution to, many agent problems.

There is [increasing discussion](https://arxiv.org/abs/2602.11988) about whether
repository context files — `CLAUDE.md`, `AGENTS.md`, `.cursorrules` — actually
help agent performance or hurt it. The findings are uncomfortable: agents given
context files that describe code state tend to trust those descriptions, read
less actual code, and perform _worse_ when the descriptions drift even slightly.
The cost goes up, the success rate goes down.

And yet — anyone who has worked with coding agents on a real project knows the
agent needs _something_. Agents left to read source files with no guidance will
default to their training: generic naming conventions, standard patterns, no
awareness of project-specific constraints or the mistakes the agent will make in
a given domain. The result is code that compiles and passes basic tests but
doesn't match how the project actually works. Conventions, non-obvious pitfalls,
design rationale that isn't in the code — these things genuinely help agents
produce correct changes on the first try.

This is a tough needle to thread. The `context-db-manual` SKILL.md tries to
address it head-on:

```
Context files describing information an agent can determine by using
find, grep, and read can be harmful to agent performance. Only document
what the code can't tell you.
```

The principle: context-db should contain the gap between what the code shows and
what the agent needs to know. Conventions the agent wouldn't infer. Pitfalls it
will hit. Rationale that isn't visible in the source. Everything else — code
summaries, architecture descriptions, module inventories — is noise that
displaces code the agent could read instead.

The hierarchical structure helps too. A flat 5,000-line `CLAUDE.md` loaded every
session forces every agent to read through database indexing rules when it's
working on CSS. The B-tree means agents navigate to relevant topics and skip the
rest — the context cost is proportional to the task, not the total knowledge
base.

Keeping context-db healthy requires active maintenance. The
[`/context-db-maintain`](#maintenance-skills) skill exists for this — its
default posture is to cut, leaving the knowledge base smaller and sharper after
each pass. Without regular maintenance, any knowledge base drifts toward the
bloated state it was designed to avoid.

## Maintenance Skills

Two optional skills help keep the knowledge base healthy over time:

**`/context-db-reindex`** — Re-reads every file, rewrites all `description`
fields in frontmatter to match current content, and creates any missing
`<folder-name>.md` descriptor files. Works bottom-up so parent folder
descriptions reflect their children. Mostly automated — asks only when a file's
purpose is genuinely ambiguous. Accepts an optional folder path to scope the
reindex.

**`/context-db-maintain`** — Maintain the knowledge base: cut stale or low-value
content, remove content that can be derived from reading the code, fix
structural problems and doc drift, check for coverage gaps, then reindex.
Default posture is to cut — leave context-db smaller and sharper. Interactive by
default. Accepts an optional folder path.

Both skills live in `templates/skills/` and can be wired into any project the
same way as the core `context-db-manual` skill.

## Documentation

Full docs: https://cart0113.github.io/context-db/

## License

MIT
