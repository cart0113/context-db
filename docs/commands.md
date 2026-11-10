# Commands

Every command prints instructions that the calling agent follows. The sections
below show the instruction text itself, included verbatim from the skill, so
this page cannot drift from what the agent reads.

Each command also inlines its `ON_*.md` file, if it has content, immediately
before the user's instruction. The instruction is always last.

## prompt

```text
/context-db prompt "add a refund endpoint"
```

Use it at the start of a piece of work, and again whenever a long session has
drifted from the project's conventions. The output is, in order:

1. The navigation rules below.
2. **Bundles**: the project bundle and every background bundle, each with its
   description and where to start reading.
3. **Work In Progress**: every file in `wip/` with its description and branch.
4. The contents of `ON_PROMPT.md`.
5. The user's instruction.

```{literalinclude} ../skill/context-db/prompts/prompt.md
:language: markdown
```

## update

```text
/context-db update
/context-db update "the retry cap is deliberate, see the incident"
/context-db update --commit
/context-db update --push
```

Use it at the end of a session. With no instruction the agent reviews the
session itself. `--commit` then commits every file touched in the session;
`--push` commits and pushes.

```{literalinclude} ../skill/context-db/prompts/update.md
:language: markdown
```

With `--commit` or `--push` this follows:

```{literalinclude} ../skill/context-db/prompts/commit.md
:language: markdown
```

## wip

```text
/context-db wip "we are adding refunds; partial refunds are out of scope"
/context-db wip
```

`<name>-project/wip/` holds the plans for work in progress. `wip` is a form of
`prompt` aimed at that folder. Besides the instructions it prints the current
branch, uncommitted changes, the commits and changed files since the main
branch, and every wip file, so the agent can tell what has landed.

```{literalinclude} ../skill/context-db/prompts/wip.md
:language: markdown
```

## configure

```text
/context-db configure
```

Run it once per repository, and again whenever something is missing. It prints
what it detected: the interpreter, the repository name, the main branch, both
config files, existing project bundles, and any leftovers from v0.0.

```{literalinclude} ../skill/context-db/prompts/configure.md
:language: markdown
```

## The ON files

`context-db/context-db-on-markdown/` holds one optional file per command:
`ON_PROMPT.md`, `ON_UPDATE.md`, `ON_WIP.md`, `ON_CONFIGURE.md`. Whatever a file
contains, outside HTML comments, is inlined every time its command runs. Keep
them to the few rules the agent must see every single time; each line is paid
for on every run.

## Helpers

Two more sub-commands do deterministic file work. Agents run them when the
instructions say to; they are also useful by hand and in CI.

`init [--project NAME] [--python CMD] [--main-branch BRANCH] [--local KEY=VALUE]`
: Writes the config and creates whatever is missing without overwriting.

`index [bundle] [--check]`
: Regenerates every `index.md` in a bundle and lints it. With no argument it
  works on the project bundle. `--check` changes nothing and exits 1 if anything
  is out of date or invalid.
