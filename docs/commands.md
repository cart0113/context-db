# Commands

There are five commands: `prompt`, `update`, `wip`, `maintain`, and
`configure`. `/context-db --help` lists them. Each one prints a set of
instructions, and the agent follows them. Nothing is hidden: the exact text is
under each command below, and
[What each command sends](#what-each-command-sends) shows the whole message.
Add `--show-context` to any command and the agent
[shows you that message](#see-the-message-for-your-own-project) for your own
project.

In Claude Code you type a command as `/context-db <command>`, and these pages
write every command that way. Other agents invoke a skill their own way. To
tell the agent something, start a new line and write it there. It needs no
quotes, and it can run to as many lines as you like.

From a terminal, run the script in the skill folder:

```bash
python3 .claude/skills/context-db/context-db.py <command>
```

## A command is a starting point

A command opens a conversation with the instructions you would otherwise type
yourself, every time: where the knowledge base is, how to read it, what
belongs in it, and what to leave out. That is all context-db does. It saves
you from saying the same things again whenever you want an agent to read or
write what your project knows.

So each command is a common default, and the rest is yours to say. `prompt`,
`update`, and `maintain` cover the whole knowledge base: the plans for work in
progress, your project knowledge, and your usage folders. No flag narrows
that. When you want something narrower, or something different, say
so in plain words, on the line after the command:

```text
/context-db update

Only the usage folder. The refund endpoint now needs an idempotency key.
```

```text
/context-db maintain

Leave the plans alone this time, and do not read the git history.
```

You can also say it later. A command only starts the conversation, and the
agent keeps listening after it: tell it to look somewhere else, to go
further, or to stop.

| Command | What it does unless you say otherwise | Things you might say |
| --- | --- | --- |
| `prompt` | Reads what bears on the task: the plans, your project knowledge, and the usage knowledge of any project the task involves. | "Carry on with the refund endpoint." "Ignore the plans, this is unrelated." |
| `update` | Works from what the agent remembers of this session. Writes the plan the session worked from, your project knowledge, and your usage folders if you have any. | "Also read `git diff main`. I changed the retry code by hand." "Only the usage folder." |
| `maintain` | Goes through the whole knowledge base, and compares it with the code and the git history. | "Only `data-model/`." "Do not read the git history." |

`update` and `maintain` differ in how far they look. `update` records what one
session learned, from what the agent remembers of it, and reads no git
history. `maintain` is a spring cleaning: it takes a broad view of the whole
knowledge base and compares it with the project as it is now, using the git
history to see what has moved. Run `update` after most sessions, and
`maintain` rarely.

## The no-duplication rule

The knowledge base does not duplicate information found in your project's
assets: the code, its comments, the configs, and your docs. A copy goes out of
date, and the next agent trusts it. `prompt`, `update`, `wip`, and `maintain`
all send the agent this text:

```{literalinclude} ../skill/context-db/prompts/no-duplication.md
:language: markdown
```

`update` follows it when it writes. `maintain` enforces it: it compares notes
with the code they describe and removes what the code already says.

## The keep-small rule

Every note has a cost. Each later session reads past it, and someone has to
keep it true as the code changes. An agent does not weigh that cost by itself,
because its task is over once the note is written. So `update`, `wip`, and
`maintain` also send the agent this text:

```{literalinclude} ../skill/context-db/prompts/keep-small.md
:language: markdown
```

It makes a smaller knowledge base count as a result, and it tells the agent to
ask you when it cannot tell whether something is still needed.

## /context-db prompt

```text
/context-db prompt

Users report a bug here:

https://issues.example.com/PAY-482

It looks like it is in the new receipts database code.
Can you investigate and propose a fix?
```

Use it before a task, or to ask a question. Use it again whenever a long
session has drifted away from your project's rules.

What the agent does:

1. Reads the plans listed in `wip/wip.md` that bear on the task, if there are
   any. The work in progress comes first.
2. Lists the project folder, with `toc`. Your project knowledge comes second,
   on every task, because it applies to everything done in your repository.
3. Lists any other folder whose description matches the task: a background
   folder of standards, or the usage folder of a project that the task
   involves. These come last. They are in `context-db/`, or anywhere else
   that your settings point to as [global context](layout.md#global-context).
4. Opens only the files whose descriptions match the task, and lists a
   subfolder only when its description matches.
5. Gets on with the task, and checks what it read against the code.

The agent is given that order in three numbered lines, and it is the same on
every `prompt`. When the knowledge base and the code disagree, the agent is
told to trust the code and to tell you.

The usage knowledge of another project is read the same way as your own
notes, with the same listing and the same short files. When a task involves a
project that yours uses, the agent is told to look into that project's usage
folder before it reads that project's code.
[How another project reads it](layout.md#how-another-project-reads-it) shows
what the agent sees.

To carry on with work that has a [plan](#context-db-wip), name the work. The
agent sees the list of plans on every `prompt`, and reads the plan for that
work before anything else:

```text
/context-db prompt

Carry on with the refund endpoint.
```

### See what the agent read

Add `--audit` to see what the agent took from the knowledge base for a task,
and how it got there. It is for whoever designs the knowledge base:

```text
/context-db prompt --audit

How should a refund be posted to the ledger?
```

What the agent does:

1. Reads the knowledge base as it does on any `prompt`. It has not yet been
   told what the report holds, so the report cannot change what it reads.
2. Runs a helper, `audit`, which tells it what to report.
3. Shows you the report, and gets on with the task.
4. Ends its reply with a second report, on what the task itself showed.

The first report is the trail. It names every folder the agent listed and
every file it opened, in order, each with what led the agent there and what
the agent took from it. A file that turned out not to matter is in it too.
The report then says what came from outside your project, such as a
background folder or global context, what the agent looked for and did not
find, and which descriptions misled it or left it unsure. This one is from the
[example project](https://github.com/cart0113/context-db/tree/v0.1/example),
shortened:

```text
context-db audit

Trail:
1. context-db/acme-payments-project/wip/refund-endpoint.md, opened. Led by
   the Work In Progress section. Took: refunds are queued, not inline, and
   the queue consumer and the ledger entry are still to do.
2. context-db/acme-payments-project/, listed. Led by the reading order: the
   project folder is listed on every task.
3. context-db/acme-payments-project/architecture.md, opened. Led by its
   description, which names the ledger. Took: services talk only through the
   message queue.
4. ../acme-ledger-repo/okf/acme-ledger-usage/, listed. Led by the Global
   Context section: the instruction involves the ledger.
5. ../acme-ledger-repo/okf/acme-ledger-usage/posting.md, opened. Led by its
   description in the listing. Took the three posting rules, and a pointer to
   the ledger API page, which was not fetched.
6. context-db/acme-payments-project/data-model/, listed. Led by its
   description, which names the refund entity.
7. context-db/acme-payments-project/data-model/entities.md, opened. Led by
   its description. Took: a refund's amount is a decimal, with no unit given.

From outside this project: steps 4 and 5, a Global Context folder in another
repository. No background folder was opened, and no web page.

Looked for and not found: which accounts a refund debits and credits. The
description of entities.md ("including amounts in minor units") made me
expect the unit of a refund's amount, and the file gives it only for a
payment. The description of acme-payments-usage ("asynchronous refunds") left
me unsure whether it bore on this.
```

The second report says what else the agent read while it worked, which files
the work rested on in the end and which it did not need, what the agent had
to guess because nothing said it, and any note that the code contradicted.
For the same question:

```text
context-db audit, after the work

Further steps in those folders: none.

The work rested on posting.md, refund-endpoint.md, and entities.md.
architecture.md added nothing that the plan had not already said.

Guessed: which accounts to debit and credit for a refund, and whether the
consumer reaches the ledger through the queue or through its API. No note
says, and the repository has no ledger code.
```

Read both as a list of things to fix. A file that was opened and not needed
has a description that promises too much. A long trail to one fact means that
the fact is hard to find. Something the agent had to guess may be a note worth
writing.

To act on it, run `update` or `maintain` in the same session and say what you
saw:

```text
/context-db maintain

Look at the audit result above. It is not good that the agent had to guess
which accounts a refund debits and credits, and that the description of the
usage folder made it wonder whether the folder was about posting.
```

The report is the agent's own account. The commands it ran and the files it
opened are in the session, if you want to check one against the other.

:::{dropdown} The text the agent receives
:color: secondary

Words in braces are filled in when the command runs. After this text the agent
sees [the no-duplication rule](#the-no-duplication-rule), the list from
`wip/wip.md` when it lists anything, the folder list, the global context
when there is any, your `ON_PROMPT.md` rules, and your instruction.

```{literalinclude} ../skill/context-db/prompts/prompt.md
:language: markdown
```

With `--audit`, the message also tells the agent to run the `audit` helper
once it has done its reading. The helper then prints this:

```{literalinclude} ../skill/context-db/prompts/audit.md
:language: markdown
```
:::

## /context-db update

```text
/context-db update
```

Use it at the end of a session. It records what that session learned, from
what the agent remembers of it. It reads no git history and does not go
through the rest of the knowledge base. [`maintain`](#context-db-maintain)
does both.

What the agent does:

1. Decides whether the knowledge base needs to change at all. Most of the time
   it does not, and the agent stops there.
2. If the session worked from a plan in `wip/`, brings that plan up to date,
   and deletes it once the work is finished.
3. If it learned something the next agent would need, finds the right file in
   the project folder, or creates one.
4. If a note it read during the session turned out to be wrong, or only
   repeated the code, fixes or deletes that note.
5. If you have a [usage folder](#usage-knowledge) and the session changed what
   other projects need to know, updates that folder as well.
6. Leaves everything else alone. If it came across other notes that look out
   of date or no longer needed, it names them and asks you whether to clean
   them up. When it is not obvious how much to clean up, it asks you how far
   to go.
7. Reads its change once more and cuts every line the next agent would not
   miss.
8. Checks the format with `toc --check`, fixes what its change caused, and
   tells you what it added, changed, and deleted.
9. With `--commit`, commits everything that changed in the session. With
   `--push`, pushes as well.

When what it learned belongs somewhere else, it says so and writes no note: a
fact about one piece of code belongs in a comment, a new plan is written by
[`wip`](#context-db-wip), and what it learned about using another project
belongs in that project's usage folder.
[Where each thing goes](layout.md#where-each-thing-goes) has the whole list.

Typed with nothing after it, the agent looks back over the session and decides
for itself what to record. To say what should be recorded, write it on a new
line:

```text
/context-db update

The retry cap of three is deliberate.
A fourth retry caused the duplicate refunds in March.
```

The same line is where you change how `update` works. It goes by what the
agent remembers, so work the agent did not see is not in it. When you changed
files by hand, or another session did, say where to look:

```text
/context-db update

Also read `git diff main`. I reworked the retry code by hand.
```

After an update you often want to commit, and perhaps push. Two flags save
you asking for that. They go on the same line as the command:

```text
/context-db update --push
```

`--commit` commits everything the session changed and does not push. `--push`
commits and pushes. Both are a convenience and a matter of preference. With
neither, `update` makes no commit, and you commit when and how you like.

### Usage knowledge

`update` writes two kinds of knowledge. Project knowledge is for agents
working on your project, and it goes in the project folder. Usage knowledge
is for agents working in other projects that use yours, and it goes in your
[usage folders](layout.md#usage-folders).

A project that nothing else uses needs no usage folder, and `update` never
starts one unasked. To start one, say so:

```text
/context-db update

Start a usage folder. Other teams call the refunds API, and they keep
getting the idempotency key wrong.
```

From then on, every `update` looks after that folder as well. What the agent
does there:

1. Decides whether an agent in another project would use yours wrongly, or
   fail to use it, without something that is not written down yet. Mostly the
   answer is no.
2. Writes the bare minimum: where to start, which way in is right for which
   job, the rules a caller must follow, and the mistakes callers make.
3. Leaves out what your project already tells its users. It does not reprint
   your API, your flags, or your docs. It says where they are.
4. Leaves out project knowledge, such as why the project is built the way it
   is. That stays in the project folder.
5. Fixes what the session made untrue, such as a rule for callers that has
   changed.

With [more than one usage folder](layout.md#more-than-one), the agent puts
each note in the folder whose readers need it, and never starts a usage
folder that your settings do not name.

:::{dropdown} The text the agent receives
:color: secondary

```{literalinclude} ../skill/context-db/prompts/update.md
:language: markdown
```

When you have a usage folder, this follows:

```{literalinclude} ../skill/context-db/prompts/update-usage.md
:language: markdown
```

The agent also receives [the no-duplication rule](#the-no-duplication-rule),
[the keep-small rule](#the-keep-small-rule), and the format rules:

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

A plan is rewritten, never added to. Each time the command runs, the agent puts
in what is new and takes out what is done or settled, so a plan gets shorter as
the work lands.

`prompt` shows the list every time it runs, so each new session starts by
knowing what is in progress. When the list is empty, `prompt` leaves it out.

Once a plan exists, the everyday commands look after it:

| When | Typed | What happens to the plan |
| --- | --- | --- |
| Before a session on that work | `/context-db prompt`, with a task that names the work | The agent reads the plan before anything else, and goes on from where it stands. |
| After the session | `/context-db update` | The agent brings the plan up to date from what the session did, and deletes it once the work is finished. |
| Rarely | `/context-db maintain` | The agent checks every plan as part of its sweep, the way `wip --maintain` does. |

The `wip` command itself is for everything else:

| Typed | What the agent does |
| --- | --- |
| `/context-db wip` | Writes or updates the plan for the current work, and its line in `wip.md`. Use it to start a plan, or to save where the work stands in the middle of a session. |
| `/context-db wip --list` | Shows what is in progress and how long each piece has been going. Changes nothing. |
| `/context-db wip --maintain` | Checks every plan against git, whichever session wrote it. Deletes the plans for work that has been merged into the main branch, and brings the other lines up to date. Anything worth keeping for the long term is moved into the main knowledge base first. |
| `/context-db wip --clear` | Shows you every plan, asks you to confirm, then deletes them all and empties the list. |

### Feature branches

A plan works well with a feature branch. Create a branch for the work, run
`/context-db wip` there, and commit the plan and its line in `wip.md` on that
branch. The list there is then about that work, and the list on the main
branch stays as it was.

When you merge, the plan must not stay in the main branch's list. There are
two ways to see to that:

- Before the merge, run `/context-db update` or `/context-db wip` on the
  branch once the work is finished. The agent deletes the plan and its line,
  and the merge brings neither with it.
- After the merge, run `/context-db wip --maintain` on the main branch. The
  agent sees that the work was merged, and deletes the plan and its line.

The agent is told this pattern as well. It is the last part of the text
below.

:::{dropdown} The text the agent receives
:color: secondary

For `/context-db wip`, followed by the list, the rules below, the
no-duplication and keep-small rules, the format rules, your `ON_WIP.md`, and
your instruction:

```{literalinclude} ../skill/context-db/prompts/wip.md
:language: markdown
```

For `--list`:

```{literalinclude} ../skill/context-db/prompts/wip-list.md
:language: markdown
```

For `--maintain`:

```{literalinclude} ../skill/context-db/prompts/wip-maintain.md
:language: markdown
```

How the plans are checked, followed by the state of git. `maintain` receives
both as well, when there are plans:

```{literalinclude} ../skill/context-db/prompts/wip-check.md
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

## /context-db maintain

```text
/context-db maintain
```

```text
/context-db maintain

Look at data-model/. It has grown.
```

Run it rarely, as a spring cleaning, or when a part of the knowledge base feels
cluttered. `update` records one session. `maintain` takes a broad view of the
whole knowledge base and compares it with the project as it is now. With
nothing after it, the agent goes through all of it: the plans, the project
folder, and your usage folders. You can name a folder or a topic instead.

A knowledge base only grows unless someone cuts it back. Notes are added one
session at a time, the project moves on, and what mattered then matters less
now. `maintain` is the sweep that cuts it back.

Its main job is to enforce [the no-duplication rule](#the-no-duplication-rule).
`update` keeps to the rule when it writes one note; `maintain` goes through the
notes looking for where it has been broken.

What the agent does:

1. Checks first. If nothing needs changing, it says so and stops.
2. Checks the plans in `wip/`, if there are any, as
   [`wip --maintain`](#context-db-wip) does.
3. Goes on to the notes, and starts with the ones the code has moved furthest
   past, which [the git history](#git-history) shows.
4. Opens the code each note talks about, comments included. It deletes what the
   code, its comments, or your docs already say, and links to them instead.
5. Lists facts about one piece of code that would be better as a comment next
   to it, as suggestions. It does not edit your code.
6. Fixes what has drifted from the code.
7. Removes what is no longer needed: notes about work that is finished, code
   that is gone, or a decision that was reversed. Cuts notes that say more
   than the next agent needs down to the fact and its reason.
8. Splits files that have grown too long or that hold several topics, groups a
   crowded folder into subfolders, merges files on the same topic, and
   rewrites vague descriptions.
9. Goes through your [usage folders](layout.md#usage-folders), if you have
   any, for their own reader: an agent in another project that uses yours and
   does not read its insides. It deletes what your README, your docs, and your
   help text already tell that reader, and moves project knowledge to the
   project folder.
10. Asks you before deleting anything that is not plainly wrong or a plain copy
    of the code.
11. Fixes the links to anything it moved, and tells you what it changed and why.

`update` does not sweep. It changes the files that the session's lesson belongs
in and the notes the session showed to be wrong, and it asks you about anything
else it noticed, so that recording one fact never turns into a reorganization.

### Git history

`maintain` takes it that your project is in git, and uses git to find what has
gone out of date. The agent is handed two things, read from git when the
command runs:

- Every note, with the date it last changed, how many commits have changed
  the project since, and which of the files it links to have changed since.
  The notes the code has moved furthest past come first.
- When there are plans, the state of git: the current branch, the uncommitted
  changes, and the commits that are not on the main branch.

The agent starts at the top of that list, reads what changed, and fixes or
deletes what is now out of date. An old note is not wrong for being old. The
agent changes only what the history and the code show.

Outside a git repository, the agent is told that there is no history, and it
works from the files alone. To leave git out where there is one, say so:

```text
/context-db maintain

Do not read the git history. Compare the notes with the code as it is.
```

:::{dropdown} The text the agent receives
:color: secondary

After this text the agent sees the no-duplication rule, the keep-small rule,
how to check the plans when there are any, the git history, the folder list,
how to check the usage folders when you have any, the format rules, your
`ON_MAINTAIN.md`, and your instruction.

```{literalinclude} ../skill/context-db/prompts/maintain.md
:language: markdown
```

The git history comes with this text:

```{literalinclude} ../skill/context-db/prompts/maintain-git.md
:language: markdown
```

When `wip/` holds a plan, the agent receives how the plans are checked, which
is shown under [`wip`](#context-db-wip). When you have a usage folder, it
receives this:

```{literalinclude} ../skill/context-db/prompts/maintain-usage.md
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
   - When it is not obvious how much to clean up after a task, should the
     agent ask you, clean up without asking, or delete nothing without asking?
   - Which other repositories does this project rely on?
   - Should `prompt` also list knowledge folders that are kept outside
     `context-db/`, such as the usage folders of other projects?
   - If other code depends on this project: where should the notes for the
     projects that use it be kept?
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

## Rule files

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

## Setting flags

`configure` asks nothing when you pass it a setting. It writes the settings,
creates whatever is missing, and never overwrites a file:

```bash
python3 .claude/skills/context-db/context-db.py configure --project acme-payments
```

Its options are `--project`, `--main-branch`, `--python`, `--usage-folder`,
`--global-context`, and `--local KEY=VALUE` for a setting that applies only
to you. Give `--usage-folder` or `--global-context` once for each value.
[Setup](setup.md#settings) describes each setting.

## The `toc` helper

context-db keeps no `index.md` files. Whenever the agent looks into the
knowledge base, it runs a small helper that lists a folder on the spot, one line
for each file and subfolder with its description:

```bash
python3 .claude/skills/context-db/context-db.py toc context-db/acme-payments-project
```

Every command that reads the knowledge base gives the agent this text, so it
always navigates the same way:

```{literalinclude} ../skill/context-db/prompts/navigate.md
:language: markdown
```

With `--check`, `toc` checks the [format](layout.md) instead: frontmatter,
links, the sizes of descriptions, files, and folders, and plans that
`wip/wip.md` does not list. The agent runs it at the end of `update`, `wip`,
`configure`, and `maintain`.

You do not need to type either, which is why `toc` is not in `--help`. The one
place to type it is CI:

```bash
python3 .claude/skills/context-db/context-db.py toc --check
```

With no folder after it, `toc --check` checks the project folder, and each
usage folder that is kept outside it.

You can [keep `index.md` files](layout.md#keeping-index-md-files-anyway) as
well, the standard OKF way. `toc` still lists your own folders from their
files, and the check warns when an index no longer matches its folder. A folder
that comes from somewhere else may bring an `index.md` of its own. `toc` prints
that file for such a folder, and builds the listing only when there is none.

[Dynamic indexing](layout.md#dynamic-indexing) describes the listing, and the
[OKF page](okf.md#dynamic-indexing) why context-db builds it on demand.

## What each command sends

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
`context-db/` alone unless you chose otherwise in `configure`. An agent that
supports skills also shows it the skill's name and one-line description, as it
does for every skill.
Each command then sends its own text and no other command's.

There is one exception, and it is yours to choose. The `ON_PROMPT.md` that
`configure` creates lets the agent run `update` on its own after a `prompt`,
when it learns something worth keeping. `configure` asks whether you want that.
If you do not, that file says so and the agent writes only when you type
`/context-db update`.

When you type a command, this happens:

1. The agent loads `SKILL.md` from the skill folder. It is short and
   says one thing: run the script with what the user typed.
2. The agent runs `context-db.py` with the command and your instruction.
3. The script prints one message, made of the sections listed below.
4. The agent follows that message. From then on it reads only what it asks for:
   folder listings from `toc`, and the notes it chooses to open.

Every section of that message comes from one of five places:

| Comes from | What it is | Who changes it |
| --- | --- | --- |
| `prompts/` in the skill folder | The canned text: built-in instructions, one file for each section. They are the same in every project, and the dropdowns above show each one. | Nobody. They come with context-db. |
| `context-db/configuration/ON_<COMMAND>.md` | [The project's rules](#rule-files) for that one command, shared with everyone. | You and your team, by hand. |
| `context-db/configuration/ON_<COMMAND>.local.md` | Your own rules for that command. Gitignored. | You, by hand. |
| Your repository, read when the command runs | The list of work in progress, the list of folders with their descriptions, the global context that your settings point to, and the state of git. | Nobody directly. It is whatever the files say at that moment. |
| What you typed | Your instruction. It always comes last. | You. |

These are the sections each command sends, in order. Each one starts with the
heading shown.

`/context-db prompt` sends:

| The agent sees | It comes from |
| --- | --- |
| `# context-db Prompt` | `prompts/prompt.md` |
| `# How to Navigate context-db` | `prompts/navigate.md` |
| `# No Duplication` | `prompts/no-duplication.md` |
| `# Work In Progress` | The list in `wip/wip.md`. Left out when it lists nothing. |
| `# Folders` | The project folder, your usage folders if there are any, and each background folder, one line each with its description. |
| `# Global Context` | Each folder outside `context-db/` that the `global_context` setting matches, one line each with its description. Left out when nothing matches. |
| `# Audit` | One step: run the `audit` helper once the reading is done. Only with `--audit`. |
| `# Project Rules` | `configuration/ON_PROMPT.md` |
| `# User Rules` | `configuration/ON_PROMPT.local.md`, if you have one. |
| `# User Instruction` | What you typed. |

With `--audit`, the helper that the agent runs after its reading prints one
more section, `# context-db Audit`, from `prompts/audit.md`.

`/context-db update` sends:

| The agent sees | It comes from |
| --- | --- |
| `# context-db Update` | `prompts/update.md` |
| `# Usage Knowledge` | `prompts/update-usage.md`. Only when you have a usage folder. |
| `# No Duplication` | `prompts/no-duplication.md` |
| `# Keep context-db Small` | `prompts/keep-small.md` |
| `# How to Navigate context-db` | `prompts/navigate.md` |
| `# Folders` | The project folder, your usage folders if there are any, and each background folder, one line each with its description. |
| `# File Format` | `prompts/format.md` |
| `# Commit` | `prompts/commit.md`. Only with `--commit` or `--push`. |
| `# Project Rules` | `configuration/ON_UPDATE.md` |
| `# User Rules` | `configuration/ON_UPDATE.local.md`, if you have one. |
| `# User Instruction` | What you typed, if anything. |

`/context-db wip` sends:

| The agent sees | It comes from |
| --- | --- |
| `# context-db Wip` | `prompts/wip.md` |
| `# Work In Progress` | The list in `wip/wip.md`, or one line saying that nothing is recorded. |
| `# How Work In Progress Is Kept` | `prompts/wip-format.md` |
| `# No Duplication` | `prompts/no-duplication.md` |
| `# Keep context-db Small` | `prompts/keep-small.md` |
| `# How to Navigate context-db` | `prompts/navigate.md` |
| `# File Format` | `prompts/format.md` |
| `# Project Rules` | `configuration/ON_WIP.md` |
| `# User Rules` | `configuration/ON_WIP.local.md`, if you have one. |
| `# User Instruction` | What you typed, if anything. |

With a flag, the first section is that flag's own instructions instead:
`prompts/wip-list.md`, `prompts/wip-maintain.md`, or `prompts/wip-clear.md`.
`--list` sends only that, the list, and your rules. `--maintain` sends every
section in the table, and adds two after the first: `# How to Check the Plans`,
from `prompts/wip-check.md`, and `# Git State`, which is the current branch,
the uncommitted changes, and the commits that are not on the main branch.
`--clear` sends its instructions, the list, `# How Work In Progress Is Kept`,
and your rules.

`/context-db maintain` sends:

| The agent sees | It comes from |
| --- | --- |
| `# context-db Maintain` | `prompts/maintain.md` |
| `# No Duplication` | `prompts/no-duplication.md` |
| `# Keep context-db Small` | `prompts/keep-small.md` |
| `# How to Navigate context-db` | `prompts/navigate.md` |
| `# How to Check the Plans` | `prompts/wip-check.md`. Only when `wip/` holds a plan. |
| `# Git State` | The current branch, the uncommitted changes, and the commits that are not on the main branch. Only when `wip/` holds a plan. |
| `# Work In Progress` | The list in `wip/wip.md`. Only when `wip/` holds a plan. |
| `# Git History` | `prompts/maintain-git.md`, then one line for each note, read from git. |
| `# Folders` | The project folder, your usage folders if there are any, and each background folder, one line each with its description. |
| `# How to Check the Usage Folders` | `prompts/maintain-usage.md`. Only when you have a usage folder. |
| `# File Format` | `prompts/format.md` |
| `# Project Rules` | `configuration/ON_MAINTAIN.md` |
| `# User Rules` | `configuration/ON_MAINTAIN.local.md`, if you have one. |
| `# User Instruction` | What you typed, if anything. |

`/context-db configure` sends:

| The agent sees | It comes from |
| --- | --- |
| `# context-db Configure` | `prompts/configure.md` |
| `# Detected State` | What the script found: the Python on your machine, the repository name, the main branch, the settings, and whether `AGENTS.md` or `CLAUDE.md` mention context-db. |
| `# Current Rules` | The text of every ON file as it is now, so that the agent can show you what each one does. |
| `# Project Rules` | `configuration/ON_CONFIGURE.md` |
| `# User Rules` | `configuration/ON_CONFIGURE.local.md`, if you have one. |
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

### See the message for your own project

Add `--show-context` to any command:

```text
/context-db prompt --show-context

Add an endpoint for refunds.
```

The agent shows you the whole message that the command sends it, and does
nothing else. It reads no notes and changes no files. The flag works on all five
commands and with their other flags, so `/context-db update --push
--show-context` shows what `update --push` would send.

In a terminal you need no flag. The script prints exactly what the agent would
get:

```bash
python3 .claude/skills/context-db/context-db.py prompt "add a refund endpoint"
```

To change what the agent is told, edit the ON file for that command: the
project's file to change it for everyone, your `.local.md` file to change it for
yourself.
`settings.md` adds no text of its own. It tells the script the name of the
project folder, the Python command, the main branch, where the usage folders
are kept, and where to look for global context.
[Other settings files](setup.md#settings-from-other-files) that it names can
override any of that.
