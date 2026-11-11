# Commands

There are four commands. Each one prints a set of instructions, and the agent
follows them. Nothing is hidden: the exact text is under each command below.

In Claude Code you type a command as `/context-db <command>`. To tell the agent
something, start a new line and write it there. It needs no quotes, and it can
run to as many lines as you like.

Anywhere else, run the script:

```bash
python3 .claude/skills/context-db/context-db.py <command>
```

## /context-db prompt

```text
/context-db prompt

Users report a bug here:

https://issues.example.com/PAY-482

It looks like it is in the new receipts database code.
Can you investigate and propose a fix?
```

Use it before a task. Use it again whenever a long session has drifted away from
your project's rules.

What the agent does:

1. Reads the plans in `wip/` that bear on the task.
2. Opens the `index.md` of each knowledge folder that looks relevant.
3. Opens only the files whose descriptions match the task.
4. Gets on with the task, and checks what it read against the code.

When the knowledge base and the code disagree, the agent is told to trust the
code and to tell you.

:::{dropdown} The text the agent receives
:color: secondary

Words in braces are filled in when the command runs. After this text the agent
sees the plans in `wip/`, the folder list, your `ON_PROMPT.md` rules, and your
instruction.

```{literalinclude} ../skill/context-db/prompts/prompt.md
:language: markdown
```
:::

## /context-db update

```text
/context-db update
```

Use it at the end of a session.

What the agent does:

1. Decides whether anything is worth writing down. Most of the time nothing is,
   and it stops there.
2. If there is something, finds the right file in the project folder, or
   creates one.
3. Regenerates the `index.md` files and fixes any format problems.
4. With `--commit`, commits everything that changed in the session. With
   `--push`, pushes as well.

Typed with nothing after it, the agent looks back over the session and decides
for itself what to record. To say what should be recorded, write it on a new
line:

```text
/context-db update

The retry cap of three is deliberate.
A fourth retry caused the duplicate refunds in March.
```

`--commit` and `--push` go on the same line as the command:

```text
/context-db update --push
```

:::{dropdown} The text the agent receives
:color: secondary

```{literalinclude} ../skill/context-db/prompts/update.md
:language: markdown
```

The agent also receives the format rules:

```{literalinclude} ../skill/context-db/prompts/format.md
:language: markdown
```

With `--commit` or `--push` it receives this as well:

```{literalinclude} ../skill/context-db/prompts/commit.md
:language: markdown
```
:::

## /context-db wip

```text
/context-db wip

We are adding receipts. Emailing them is out of scope for now.
```

Use it for work that takes more than one session. Plans live in the `wip/`
folder inside the project folder.

What the agent does:

1. Reads every plan in `wip/`.
2. Looks at git: the current branch, uncommitted changes, and what has been
   committed since the main branch.
3. Deletes the plans for work that has landed, meaning merged into the main
   branch. Anything worth keeping for the long term is moved into the main
   knowledge base first.
4. Writes or updates the plan for what you are doing now.

`prompt` lists the plans in `wip/` every time it runs, so each new session
starts by knowing what is in progress.

A plan can name the branch it belongs to. The agent asks you before it touches a
plan for a different branch. Typed with nothing after it, `wip` only cleans up
and tells you what is in progress.

:::{dropdown} The text the agent receives
:color: secondary

After this text the agent sees the git state, every plan in `wip/`, the format
rules, your `ON_WIP.md`, and your instruction.

```{literalinclude} ../skill/context-db/prompts/wip.md
:language: markdown
```
:::

## /context-db configure

```text
/context-db configure
```

Run it once per repository to set things up. Run it again whenever you want the
agent to behave differently.

What the agent does:

1. Looks at what is already there: the Python on your machine, the repository
   name, the main branch, and any existing settings.
2. Asks you a few questions, one at a time, as a menu: the project name, who
   updates the knowledge base, whether to add a note for the agent to
   `AGENTS.md` or `CLAUDE.md`, and which other repositories this project relies
   on. Those repositories, by path or URL, are listed in `ON_PROMPT.md` so that
   the agent knows where to look.
3. Reads the rule files, tells you what they make the agent do today, and asks
   whether you want to change anything. You say what you want in your own
   words, and the agent edits the files and shows you the result.
4. Writes the settings and creates whatever is missing. It never overwrites
   anything.
5. Ends with a short summary: the files it changed, and the files that control
   context-db.

These are the files that control context-db:

| File | What it controls |
| --- | --- |
| `context-db/context-db.json` | Shared settings |
| `context-db/context-db.local.json` | Your own settings, if you have any |
| `context-db/context-db-on-markdown/ON_*.md` | The rules added to each command |
| `AGENTS.md` or `CLAUDE.md` | The note that keeps the agent out of the knowledge base until asked |

The question about updates has two answers. With `on-command`, the agent writes
to the knowledge base only when you run `/context-db update`. With
`agent-decides`, it also writes when it thinks it has learned something worth
keeping, and tells you each time. Your answer is written as a short paragraph
into `ON_PROMPT.md`, where you can reword it.

:::{dropdown} The text the agent receives
:color: secondary

```{literalinclude} ../skill/context-db/prompts/configure.md
:language: markdown
```
:::

## The rule files control how the agent behaves

The commands come with built-in instructions, shown in the dropdowns above. You
do not edit those. To change what the agent does, you add your own rules to four
files in `context-db/context-db-on-markdown/`. Whatever a file says is added to
the agent's instructions every time that command runs.

The easy way to change them is `/context-db configure`. It reads the files,
tells you what they say now, and asks what you want changed. You can also edit
them by hand; they are plain Markdown.

Some examples of what goes in them:

- In `ON_PROMPT.md`: "This service handles card data. Read the PCI rules before
  touching storage or logging." Or: "Never explain code unless asked."
- In `ON_UPDATE.md`: "Commit messages follow Conventional Commits." Or: "Never
  record anything about customer names."
- In `ON_WIP.md`: "Every plan lists the ticket number."

The files:

| File | Added to every |
| --- | --- |
| `ON_PROMPT.md` | `prompt` |
| `ON_UPDATE.md` | `update` |
| `ON_WIP.md` | `wip` |
| `ON_CONFIGURE.md` | `configure` |

The text is placed immediately before your instruction, which always comes
last. It appears under the heading `Project Rules`, unless your file starts with
a heading of its own.

Keep these files short, because every line is read on every run. Text inside
HTML comments is left out, so you can keep notes to yourself in them. An empty
file adds nothing.

## Two helper commands

The agent runs these when the instructions tell it to. You can run them too.

```bash
python3 .claude/skills/context-db/context-db.py init --project acme-payments
python3 .claude/skills/context-db/context-db.py index
python3 .claude/skills/context-db/context-db.py index --check
```

`init` writes the settings and creates whatever is missing. Its options are
`--project`, `--update-mode`, `--main-branch`, `--python`, and `--local
KEY=VALUE` for a setting that applies only to you.

`index` regenerates every `index.md` in the project folder and checks the
format. Give it a folder to work on a different one. With `--check` it changes
nothing and exits with an error if anything is wrong.
