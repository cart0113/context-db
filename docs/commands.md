# Commands

There are five commands: `prompt`, `update`, `wip`, `configure`, and
`maintain`. `/context-db --help` lists them. Each one prints a set of
instructions, and the agent follows them. Nothing is hidden: the exact text is
under each command below, and [How it all fits together](#how-it-all-fits-together)
shows the whole message each command sends.

In Claude Code you type a command as `/context-db <command>`. To tell the agent
something, start a new line and write it there. It needs no quotes, and it can
run to as many lines as you like.

Anywhere else, run the script:

```bash
python3 .claude/skills/context-db/context-db.py <command>
```

## The rule every command repeats

The knowledge base is not a mirror of the code. Anything an agent can learn by
reading the code and its comments stays in the code, because a copy drifts out
of date and the next agent trusts it. `prompt`, `update`, `wip`, and `maintain`
all give the agent this text, so it hears the rule every time it reads or
writes the knowledge base:

```{literalinclude} ../skill/context-db/prompts/not-a-mirror.md
:language: markdown
```

`update` follows it when it writes. `maintain` enforces it: it compares notes
with the code they describe and removes what the code already says.

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

1. Reads the plans listed in `wip/wip.md` that bear on the task, if there are
   any.
2. Lists each knowledge folder that looks relevant, with `toc`, and lists a
   subfolder only when its description matches.
3. Opens only the files whose descriptions match the task.
4. Gets on with the task, and checks what it read against the code.

When the knowledge base and the code disagree, the agent is told to trust the
code and to tell you.

:::{dropdown} The text the agent receives
:color: secondary

Words in braces are filled in when the command runs. After this text the agent
sees [the rule every command repeats](#the-rule-every-command-repeats), the list
from `wip/wip.md` when it lists anything, the folder list, your `ON_PROMPT.md`
rules, and your instruction.

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
3. Checks the format with `toc --check` and fixes what its change caused.
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

The agent also receives [the rule every command
repeats](#the-rule-every-command-repeats), the folder list, and the format
rules:

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

This command is optional. Use it for work that takes more than one session, and
ignore it otherwise; a project that never runs it loses nothing.

It keeps one short file, `wip/wip.md` inside the project folder, with one line
for each piece of work in progress: a link to its plan, the date it started, the
branch, and where it stands.

```markdown
- [Refund endpoint](refund-endpoint.md). Started 2026-11-03 on `feature/refunds`. Validation done; partial refunds undecided.
```

Most plans are one file next to `wip.md`. A large piece of work gets a folder of
its own, and its line links to the folder.

`prompt` shows the list every time it runs, so each new session starts by
knowing what is in progress. When the list is empty, `prompt` leaves it out.

| Typed | What the agent does |
| --- | --- |
| `/context-db wip` | Writes or updates the plan for the current work, and its line in `wip.md`. |
| `/context-db wip --list` | Shows what is in progress and how long each piece has been going. Changes nothing. |
| `/context-db wip --cleanup` | Looks at git, deletes the plans for work that has been merged into the main branch, and brings the other lines up to date. Anything worth keeping for the long term is moved into the main knowledge base first. |
| `/context-db wip --clear` | Shows you every plan, asks you to confirm, then deletes them all and empties the list. |

:::{dropdown} The text the agent receives
:color: secondary

For `/context-db wip`, followed by the list, the rules below, the format rules,
your `ON_WIP.md`, and your instruction:

```{literalinclude} ../skill/context-db/prompts/wip.md
:language: markdown
```

For `--list`:

```{literalinclude} ../skill/context-db/prompts/wip-list.md
:language: markdown
```

For `--cleanup`, followed by the git state:

```{literalinclude} ../skill/context-db/prompts/wip-cleanup.md
:language: markdown
```

For `--clear`:

```{literalinclude} ../skill/context-db/prompts/wip-clear.md
:language: markdown
```

How `wip.md` and the plans are kept, for every form except `--list`:

```{literalinclude} ../skill/context-db/prompts/wip-format.md
:language: markdown
```
:::

## /context-db configure

```text
/context-db configure
```

Run it first, to set context-db up in a repository, and again whenever you want
it to behave differently. `prompt`, `update`, `wip`, and `maintain` tell you to
run it if context-db is not set up yet.

`configure` is a helper. It gets context-db working and starts a short
conversation about how the agent should treat the knowledge base. Everything it
writes is plain Markdown, and you are expected to open those files afterwards
and edit them by hand until they say what you want.

What the agent does:

1. Looks at what is already there: the Python on your machine, the repository
   name, the main branch, any existing settings, and whether `AGENTS.md` or
   `CLAUDE.md` mention context-db.
2. Asks for the project name, and the main branch and Python command when it
   cannot tell. Then it writes the settings and creates whatever is missing. It
   never overwrites anything.
3. Asks a few questions, one at a time, as a menu, and writes each answer into
   the files as you give it:
   - Is this a new project, where breaking changes are fine, or does other code
     depend on it? What is it, and who uses it? This becomes a rule in
     `ON_PROMPT.md` and the description of the project folder.
   - Should the agent read the knowledge base only when you run a command?
   - Does your agent read `AGENTS.md` or `CLAUDE.md`? It adds a one-line note
     about context-db to that file.
   - May the agent update the knowledge base as it works, after `prompt`, or
     only when you run `update`?
   - When a note gets too long, should the agent split it while it is working
     in it, or only when you run `maintain`?
   - Which other repositories does this project rely on?
   - Is there anything else the agent should always do?
4. Ends with a short summary: the files it changed, and a reminder that this
   was only a first draft for you to edit.

These are the files it writes:

| File | What it controls |
| --- | --- |
| `context-db/configuration/settings.md` | Shared settings |
| `context-db/configuration/settings.local.md` | Your own settings, if you have any |
| `context-db/configuration/ON_*.md` | The project's rules, added to each command |
| `context-db/configuration/ON_*.local.md` | Your own rules, if you have any |
| `AGENTS.md` or `CLAUDE.md` | The note that tells the agent about the knowledge base |

:::{dropdown} The text the agent receives
:color: secondary

```{literalinclude} ../skill/context-db/prompts/configure.md
:language: markdown
```
:::

## /context-db maintain

```text
/context-db maintain

Look at data-model/. It has grown.
```

```text
/context-db maintain --use-git-diff
```

Run it now and then, or when a part of the knowledge base feels cluttered. With
nothing after it, the agent looks at the whole project folder; you can name a
folder or a topic instead.

Its main job is to enforce [the rule every command
repeats](#the-rule-every-command-repeats). `update` keeps to the rule when it
writes one note; `maintain` goes through the notes looking for where it has been
broken.

What the agent does:

1. Checks first. If nothing needs changing, it says so and stops.
2. Opens the code each note talks about, comments included. It deletes what the
   code or its comments already say, and links to the code instead.
3. Lists facts about one piece of code that would be better as a comment next
   to it, as suggestions. It does not edit your code.
4. Fixes what has drifted from the code.
5. Splits files that have grown too long, groups a crowded folder into
   subfolders, merges files on the same topic, and rewrites vague descriptions.
6. Asks you before deleting anything that is not plainly wrong or a plain copy
   of the code.
7. Fixes the links to anything it moved, and tells you what it changed and why.

With `--use-git-diff`, the agent also gets the git history: every note, with
the date it last changed, how many commits have changed the project since, and
which files it links to have changed since. It starts with the notes the code
has moved furthest past, reads what changed, and fixes or deletes what is now
out of date. An old note is not wrong for being old; it changes only what the
history and the code show.

`update` does none of this. It only touches the files that the session's lesson
belongs in, so that recording one fact never turns into a reorganization.

:::{dropdown} The text the agent receives
:color: secondary

After this text the agent sees the rule every command repeats, the git history
when you ask for it, the folder list, the format rules, your `ON_MAINTAIN.md`,
and your instruction.

```{literalinclude} ../skill/context-db/prompts/maintain.md
:language: markdown
```

With `--use-git-diff`, the history comes with this text:

```{literalinclude} ../skill/context-db/prompts/maintain-git.md
:language: markdown
```
:::

## The rule files control how the agent behaves

The commands come with built-in instructions, shown in the dropdowns above. You
do not edit those. To change what the agent does, you add your own rules to five
files in `context-db/configuration/`. Whatever a file says is added to the
agent's instructions every time that command runs.

They are plain Markdown. Edit them by hand. `/context-db configure` writes a
first version and can change them for you, but there is nothing it does that
you cannot do in an editor.

Some examples of what goes in them:

- In `ON_PROMPT.md`: "This service handles card data. Read the PCI rules before
  touching storage or logging." Or: "Never explain code unless asked."
- In `ON_UPDATE.md`: "Commit messages follow Conventional Commits." Or: "Never
  record anything about customer names."
- In `ON_WIP.md`: "Every plan lists the ticket number."

Each file is named after its command, so the name says when the agent sees it:
`ON_PROMPT.md` is added to every `prompt`, `ON_UPDATE.md` to every `update`, and
so on.

The text is placed near the end, just before your instruction, which always
comes last. It appears under the heading `Project Rules`, unless your file
starts with a heading of its own.

Keep these files short, because every line is read on every run. Text inside
HTML comments is left out, so you can keep notes to yourself in them. An empty
file adds nothing.

### Project rules and your own rules

Those five files are committed, so everyone who works on the project gets the
same rules. For a rule that is only yours, make a file with the same name ending
in `.local.md`, next to the project's file:

| The project's rules, committed | Your own rules, gitignored | Added to every |
| --- | --- | --- |
| `ON_PROMPT.md` | `ON_PROMPT.local.md` | `prompt` |
| `ON_UPDATE.md` | `ON_UPDATE.local.md` | `update` |
| `ON_WIP.md` | `ON_WIP.local.md` | `wip` |
| `ON_CONFIGURE.md` | `ON_CONFIGURE.local.md` | `configure` |
| `ON_MAINTAIN.md` | `ON_MAINTAIN.local.md` | `maintain` |

Your file is added after the project's, under the heading `User Rules`. The
agent is told that where the two differ, yours wins. Use it for how you like to
work: "Answer in one paragraph." Or: "Ask before running the test suite, it is
slow on this machine." None of these files exist until you make them.

Settings work the same way: `settings.md` is the project's, and
`settings.local.md` is yours. So one pattern covers every file that is yours
alone, and one line in `.gitignore` keeps them all out of git:

```text
context-db/configuration/*.local.md
```

`configure` adds that line for you. To check that a file is ignored:

```bash
git check-ignore -v context-db/configuration/ON_PROMPT.local.md
```

## Setting up without questions

`configure` asks nothing when you pass it a setting. It writes the settings,
creates whatever is missing, and never overwrites a file:

```bash
python3 .claude/skills/context-db/context-db.py configure --project acme-payments
```

Its options are `--project`, `--main-branch`, `--python`, and
`--local KEY=VALUE` for a setting that applies only to you.

## Listing and checking: toc

context-db has no `index.md` files. Whenever the agent looks into the knowledge
base, it runs a small helper that lists a folder on the spot, one line for each
file and subfolder with its description:

```bash
python3 .claude/skills/context-db/context-db.py toc context-db/acme-payments-project
```

Every command that reads the knowledge base gives the agent this text, so it
always navigates the same way:

```{literalinclude} ../skill/context-db/prompts/navigate.md
:language: markdown
```

With `--check`, `toc` checks the [format](layout.md) instead: frontmatter,
links, file and folder sizes, and plans that `wip/wip.md` does not list. The
agent runs it at the end of `update`, `wip`, `configure`, and `maintain`.

You do not need to type either, which is why `toc` is not in `--help`. The one
place to type it is CI:

```bash
python3 .claude/skills/context-db/context-db.py toc --check
```

[Dynamic indexing](layout.md#dynamic-indexing) describes the listing, and the
[OKF page](okf.md#dynamic-indexing) why context-db builds it on demand.

## How it all fits together

context-db is nothing more than context: text that is put in front of the agent
when you ask for it. Some of that text is canned. It comes with context-db and
is the same in every project. The rest is yours: the rules you write in the ON
files. A command puts the two together, adds your instruction, and prints the
result for the agent.

That is all the script does. It does not call a model and does not run in the
background. It reads files in your repository and prints text. The agent reads
that text and does the work.

You decide when that happens. Until you type a command, the agent has one line
from context-db: the note in `AGENTS.md` or `CLAUDE.md`, which tells it to leave
`context-db/` alone unless you chose otherwise in `configure`. Claude Code also
shows it the skill's name and one-line description, as it does for every skill.
Each command then sends its own text and no other command's.

There is one exception, and it is yours to choose. The `ON_PROMPT.md` that
`configure` creates lets the agent run `update` on its own after a `prompt`,
when it learns something worth keeping. `configure` asks whether you want that.
If you do not, that file says so and the agent writes only when you type
`/context-db update`.

When you type a command, this happens:

1. Claude Code gives the agent `SKILL.md` from the skill folder. It is short and
   says one thing: run the script with what the user typed.
2. The agent runs `context-db.py` with the command and your instruction.
3. The script prints one message, made of the sections listed below.
4. The agent follows that message. From then on it reads only what it asks for:
   folder listings from `toc`, and the notes it chooses to open.

Every section of that message comes from one of five places:

| Comes from | What it is | Who changes it |
| --- | --- | --- |
| `.claude/skills/context-db/prompts/` | The canned text: built-in instructions, one file for each section. They are the same in every project, and the dropdowns above show each one. | Nobody. They come with context-db. |
| `context-db/configuration/ON_<COMMAND>.md` | [The project's rules](#the-rule-files-control-how-the-agent-behaves) for that one command, shared with everyone. | You and your team, by hand. |
| `context-db/configuration/ON_<COMMAND>.local.md` | Your own rules for that command. Gitignored. | You, by hand. |
| Your repository, read when the command runs | The list of work in progress, the list of folders with their descriptions, and the state of git. | Nobody directly. It is whatever the files say at that moment. |
| What you typed | Your instruction. It always comes last. | You. |

These are the sections each command sends, in order. Each one starts with the
heading shown.

`/context-db prompt` sends:

| The agent sees | It comes from |
| --- | --- |
| `# Context-db Prompt` | `prompts/prompt.md` |
| `# How to Navigate Context-db` | `prompts/navigate.md` |
| `# Context-db Is Not a Mirror of the Code` | `prompts/not-a-mirror.md` |
| `# Work In Progress` | The list in `wip/wip.md`. Left out when it lists nothing. |
| `# Folders` | The project folder and each background folder, one line each with its description. |
| `# Project Rules` | `configuration/ON_PROMPT.md` |
| `# User Rules` | `configuration/ON_PROMPT.local.md`, if you have one. |
| `# User Instruction` | What you typed. |

`/context-db update` sends:

| The agent sees | It comes from |
| --- | --- |
| `# Context-db Update` | `prompts/update.md` |
| `# Context-db Is Not a Mirror of the Code` | `prompts/not-a-mirror.md` |
| `# How to Navigate Context-db` | `prompts/navigate.md` |
| `# Folders` | The project folder and each background folder, one line each with its description. |
| `# File Format` | `prompts/format.md` |
| `# Commit` | `prompts/commit.md`. Only with `--commit` or `--push`. |
| `# Project Rules` | `configuration/ON_UPDATE.md` |
| `# User Rules` | `configuration/ON_UPDATE.local.md`, if you have one. |
| `# User Instruction` | What you typed, if anything. |

`/context-db wip` sends:

| The agent sees | It comes from |
| --- | --- |
| `# Context-db Wip` | `prompts/wip.md` |
| `# Work In Progress` | The list in `wip/wip.md`, or one line saying that nothing is recorded. |
| `# How Work In Progress Is Kept` | `prompts/wip-format.md` |
| `# Context-db Is Not a Mirror of the Code` | `prompts/not-a-mirror.md` |
| `# How to Navigate Context-db` | `prompts/navigate.md` |
| `# File Format` | `prompts/format.md` |
| `# Project Rules` | `configuration/ON_WIP.md` |
| `# User Rules` | `configuration/ON_WIP.local.md`, if you have one. |
| `# User Instruction` | What you typed, if anything. |

With a flag, the first section is that flag's own instructions instead:
`prompts/wip-list.md`, `prompts/wip-cleanup.md`, or `prompts/wip-clear.md`.
`--list` sends only that, the list, and your rules. `--cleanup` sends every
section in the table, and adds `# Git State` after the first: the current
branch, the uncommitted changes, and the commits that are not on the main
branch. `--clear` sends its instructions, the list,
`# How Work In Progress Is Kept`, and your rules.

`/context-db configure` sends:

| The agent sees | It comes from |
| --- | --- |
| `# Context-db Configure` | `prompts/configure.md` |
| `# Detected State` | What the script found: the Python on your machine, the repository name, the main branch, the settings, and whether `AGENTS.md` or `CLAUDE.md` mention context-db. |
| `# Current Rules` | The text of every ON file as it is now, so that the agent can show you what each one does. |
| `# Project Rules` | `configuration/ON_CONFIGURE.md` |
| `# User Rules` | `configuration/ON_CONFIGURE.local.md`, if you have one. |
| `# User Instruction` | What you typed, if anything. |

`/context-db maintain` sends:

| The agent sees | It comes from |
| --- | --- |
| `# Context-db Maintain` | `prompts/maintain.md` |
| `# Context-db Is Not a Mirror of the Code` | `prompts/not-a-mirror.md` |
| `# How to Navigate Context-db` | `prompts/navigate.md` |
| `# Git History` | `prompts/maintain-git.md`, then one line for each note, read from git. Only with `--use-git-diff`. |
| `# Folders` | The project folder and each background folder, one line each with its description. |
| `# File Format` | `prompts/format.md` |
| `# Project Rules` | `configuration/ON_MAINTAIN.md` |
| `# User Rules` | `configuration/ON_MAINTAIN.local.md`, if you have one. |
| `# User Instruction` | What you typed, if anything. |

An empty ON file adds no section, and neither does a missing one. With no
instruction there is no `User Instruction` section.

This is the whole message for the `prompt` example at the top of this page, run
in the [example project](https://github.com/cart0113/context-db/tree/v0.1/example)
that comes with the repository. Its `ON_PROMPT.md` holds two rules, which are
the `Project Rules` section near the end:

:::{dropdown} Everything the agent receives for one prompt
:color: secondary

```{literalinclude} examples/prompt-output.txt
:language: markdown
```
:::

To see the message for your own project, run the same command in a terminal. It
prints exactly what the agent would get:

```bash
python3 .claude/skills/context-db/context-db.py prompt "add a refund endpoint"
```

To change what the agent is told, edit the ON file for that command: the
project's file to change it for everyone, your `.local.md` file to change it for
yourself.
`settings.md` adds no text of its own. It tells the script the name of the
project folder, the Python command, and the main branch.
