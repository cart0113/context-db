# Context-db Configure

`/context-db configure` is a helper. The user runs it first, to get context-db
working in this repository, and again whenever they want to change how it
behaves. It starts a short conversation about how the agent should treat the
knowledge base. It is not a settings system: everything it writes is plain text
that the user can read and edit by hand, and the agent reads exactly what those
files say. Keep the conversation short.

Everything it writes lives in `{conf_dir}/`:

- `{settings}`: the project name, the Python command, and the main branch, as
  `key: value` lines between the `---` lines at the top. `{local_settings}`, if
  it exists, overrides any of them for one user and is gitignored.
- `ON_PROMPT.md`, `ON_UPDATE.md`, `ON_WIP.md`, `ON_CONFIGURE.md`,
  `ON_MAINTAIN.md`: rules.
  Whatever a file says outside HTML comments is added to the instructions the
  agent receives each time that command runs.

What the script found is listed under Detected State and Current Rules below.

## How to ask

Ask one question at a time, as a menu. Use your question tool if you have one
(in Claude Code, `AskUserQuestion`); otherwise print the options as a numbered
list and wait for the answer. Put the recommended option first and mark it.
When the files already answer a question, that answer is the recommended
option. Every question also accepts an answer the user types.

If `{settings}` already exists, begin by asking what the user wants to do: go
through the questions again, change one thing (ask which), or only check that
everything is in order (go to Finish). Do only what they pick.

## Settings

1. **Project name.** "What should this project be called?" Offer the suggested
   name. The project folder will be `{cdb}/<name>-project/`.
2. **Main branch.** "Which branch is your main branch?" Offer the suggested
   branch. Skip this question when the suggestion is not marked as a guess.
3. **Python.** Ask only when Detected State says `python3` is missing or too
   old: "Which command runs Python 3.8 or newer?" Offer the suggested value, and
   ask whether it is right for the whole team or only for this machine.

Then run this, leaving out any flag whose question you did not ask, but always
passing `--project`:

    {setup_cmd} --project <name> --main-branch <branch> --python <command>

For a Python that is right only on this machine, pass `--python python3` and add
`--local python=<command>`. With these flags, configure asks nothing: it writes
the settings, creates whatever is missing without overwriting anything, and
checks the format. Fix every error it prints.

## How the agent treats the knowledge base

Make each change as soon as the user answers, and show them the new text.

4. **The project.** "Is this a new project, where sweeping changes that break
   backwards compatibility are fine, or does other code or other people depend
   on it?" Options: new, breaking changes are fine; established, keep changes
   compatible. Then ask what the project is and who uses it, in a sentence or
   two, and talk it through briefly. Use what you learn twice:
   - Put one of these rules in `ON_PROMPT.md`, or replace the one there:
     - New: "This project is new. Make breaking changes freely: rename and
       restructure directly, with no shims, aliases, or fallbacks for old names,
       and update the callers."
     - Established: "Other code and people depend on this project. Keep changes
       backwards compatible unless the user says otherwise, and point out any
       change that could break a caller."
   - Replace the `description` in the project folder's descriptor,
     `{cdb}/<name>-project/<name>-project.md`, with one or two specific lines
     that say what this project is. Change nothing else in that file.
5. **When the agent reads it.** "Should the agent read `{cdb}/` only when you
   run a `/context-db` command?" Options: only then (recommended: notes loaded
   on every task crowd out the code); also on its own, when a task needs it.
6. **A note for the agent.** Detected State says whether `AGENTS.md` and
   `CLAUDE.md` exist and mention `{cdb}/`. "Add a short note about context-db to
   your agent instructions file?" Options: the file that exists, create
   `CLAUDE.md` (Claude Code), create `AGENTS.md` (most other agents), or skip.
   The note is the text of `{agents_snippet}`. If the answer to question 5 was
   "also on its own", replace its bold sentence with: "**Read `{cdb}/` when a
   task needs this project's conventions or decisions.** List a folder with
   `{toc_cmd} <folder>`, starting at the project folder, and open only what
   bears on the task." If the file
   already has a note, offer to replace it.
7. **When the agent writes to it.** "After `/context-db prompt`, may the agent
   update the knowledge base as it works?" Options: yes, as it goes
   (recommended: what was learned is written down while it is fresh); only when
   you run `/context-db update`. `ON_PROMPT.md` holds a paragraph about this.
   Make it say the answer, replacing the one that is there:
   - As it goes: "You may update the knowledge base as you work, without being
     asked, when you learn something the next agent would get wrong without it:
     a correction from the user, a decision and its reason, a pitfall. Run
     `{update_cmd} '<what you learned>'` and follow what it prints. Keep the
     bar high, tell the user in one line each time, and never commit on your
     own."
   - Only on command: "Write to the knowledge base only when the user runs
     `/context-db update`. At any other time, leave `{cdb}/` alone. If you learn
     something worth keeping, say so in one line and suggest that command."
8. **Long files.** "When a note in the knowledge base gets too long, should
   the agent split it up as it goes, or only when you run `/context-db
   maintain`?" Options: as it goes (recommended: a file is split while someone
   is already working in it, and never in a sweep); only on maintain.
   `ON_UPDATE.md` holds a paragraph about this. Make it say the answer,
   replacing the one that is there:
   - As it goes: "When a file you are editing grows past about 150 lines, split
     it into smaller files, or a subfolder of the same name. Leave files you are
     not editing alone."
   - Only on maintain: "Do not split or reorganize files, even long ones. If a
     file you edited is now over about 150 lines, say so in one line and
     suggest `/context-db maintain`."
9. **Other repositories.** "Does this project rely on other repositories?"
   Options: no, or yes. For each one, get where it is (a path on disk or a URL)
   and one line on what this project uses it for. Record them in `ON_PROMPT.md`
   under the line "Related repositories:", one per line: name, location, what it
   is for. Replace that list if it is already there. Do not clone anything. If a
   repository is on disk and has its own `context-db/` folder, also offer to
   mount it: a symlink at the top level of `{cdb}/`, named after the folder it
   points to. A mount that is only for this user also goes in `.gitignore`.
10. **Anything else.** Tell the user in a sentence per file what the ON files
    make the agent do now. Then ask: "Is there anything else the agent should
    always do?" Options: no (recommended); yes, for `prompt` (while it works),
    `update` (what gets written down, how commits are made), `wip` (how work in
    progress is kept), or `maintain` (how the knowledge base is tidied). Ask
    them to say it in their own words.

When you write a rule, make it one or two short, direct sentences addressed to
the agent, outside the HTML comments. Keep each file short, because every line
is read on every run. A rule that matters only for some tasks belongs in the
knowledge base instead; say so.

## Finish

Run:

    {check_cmd}

It must report no errors. Then give the user a short summary, and nothing more:

- **What changed**: each file you created or edited, with a few words on what
  changed. If nothing changed, say so.
- **This was a helper.** Say plainly that configure only wrote a first draft,
  and that the user should open these files and edit them by hand until they
  say what the user wants: `{conf_dir}/` (the settings and the ON files) and the
  note in `AGENTS.md` or `CLAUDE.md`. They are plain Markdown, and there is
  nothing else to keep in step.
- **What to type**: `/context-db prompt` before work, with the task on a new
  line after it; `/context-db update` after the work. `/context-db wip` is
  optional, for keeping track of long-running work. `/context-db maintain` now
  and then tidies the knowledge base. `/context-db --help` lists them.

Do not commit; leave the changes for the user to review.
