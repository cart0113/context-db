# Commands

There are five commands: `prompt`, `update`, `wip`, `configure`, and
`maintain`. `/context-db --help` lists them. Each one prints a set of
instructions, and the agent follows them. Nothing is hidden: the exact text is under each command below.

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
| `context-db/configuration/ON_*.md` | The rules added to each command |
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

The files:

| File | Added to every |
| --- | --- |
| `ON_PROMPT.md` | `prompt` |
| `ON_UPDATE.md` | `update` |
| `ON_WIP.md` | `wip` |
| `ON_CONFIGURE.md` | `configure` |
| `ON_MAINTAIN.md` | `maintain` |

The text is placed immediately before your instruction, which always comes
last. It appears under the heading `Project Rules`, unless your file starts with
a heading of its own.

Keep these files short, because every line is read on every run. Text inside
HTML comments is left out, so you can keep notes to yourself in them. An empty
file adds nothing.

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
