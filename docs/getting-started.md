# Getting started

## 1. Install the skill

Copy the skill folder into the project. It is one script, a few prompt files,
and starter templates. It needs Python 3.8 or newer and nothing else.

```bash
git clone -b v0.1 https://github.com/cart0113/context-db /tmp/context-db
mkdir -p .claude/skills
cp -r /tmp/context-db/skill/context-db .claude/skills/context-db
```

To track updates instead of copying, symlink the folder from a checkout.

For an agent that does not read `.claude/skills/`, put the folder wherever that
agent keeps skills. The script finds its prompts relative to itself, and every
command can be run by hand:

```bash
python3 .claude/skills/context-db/context-db.py help
```

## 2. Configure

In Claude Code:

```text
/context-db configure
```

The agent proposes a project name, interpreter, and main branch, confirms them,
and runs the `init` helper. The same thing by hand:

```bash
python3 .claude/skills/context-db/context-db.py init --project acme-payments --main-branch main
```

That creates:

```text
context-db/
├── context-db.json
├── context-db-on-markdown/
│   ├── ON_PROMPT.md   ON_UPDATE.md   ON_WIP.md   ON_CONFIGURE.md
└── acme-payments-project/
    ├── acme-payments-project.md
    ├── index.md
    └── wip/
```

`init` never overwrites a file, so it is safe to run again.

### Shared and per-user config

`context-db/context-db.json` is committed:

```json
{
  "project": "acme-payments",
  "python": "python3",
  "main_branch": "main"
}
```

| Key           | Meaning                                                    |
| ------------- | ---------------------------------------------------------- |
| `project`     | The project bundle is `context-db/<project>-project/`.     |
| `python`      | The interpreter command the agent uses to run the script.  |
| `main_branch` | The branch `wip` compares the current branch against.      |

`context-db/context-db.local.json` is gitignored. Any key in it overrides the
shared value for one user. Use it for an interpreter path that exists only on
one machine:

```bash
python3 .claude/skills/context-db/context-db.py init --local python=/opt/python3.12/bin/python3
```

## 3. Tell the agent the knowledge base exists

Paste `.claude/skills/context-db/starters/AGENTS.md` into the project's
`AGENTS.md`, `CLAUDE.md`, or equivalent. It tells the agent that `context-db/`
exists and, deliberately, that it must not read it unprompted.

## 4. Use it

```text
/context-db prompt "add a refund endpoint"
... work ...
/context-db update --push
```

Add `/context-db wip "<what we are doing>"` at the start of a multi-session
effort. See [](commands.md).

## 5. Keep it honest

Add the check to a pre-commit hook or CI:

```bash
python3 .claude/skills/context-db/context-db.py index --check
```

It fails when an `index.md` is out of date or a file breaks the
[format](format.md).

A complete, runnable project is in
[`example/`](https://github.com/cart0113/context-db/tree/v0.1/example).
