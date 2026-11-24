# context-db Configure

`/context-db configure` is a helper. The user runs it first, to get context-db
working in this repository, and again whenever they want to change how it
behaves. It starts a short conversation about how the agent should treat the
knowledge base. It is not a settings system: everything it writes is plain text
that the user can read and edit by hand, and the agent reads exactly what those
files say. Keep the conversation short.

Everything it writes lives in `{conf_dir}/`:

- `{settings}`: the project name, the Python command, and the main branch, as
  `key: value` lines between the `---` lines at the top. Optional lines say
  where the usage folders are kept and where to find global context.
  `{local_settings}`, if it exists, overrides any of them for one user and is
  gitignored.
- Either of those can name more settings files on a `settings_files` line,
  such as a file a team shares between projects. A file named there is read
  after the file that names it and overrides it. The user writes that line and
  those files by hand: never create or edit them, and when a setting does not
  seem to take effect, look for it in a file that is read later. Detected
  State lists every settings file in the order it is read, and marks a line
  that is not a setting. The other commands stop on such a line, so offer to
  correct it in `{settings}` or `{local_settings}`, or tell the user which
  file to fix.
- `ON_PROMPT.md`, `ON_UPDATE.md`, `ON_WIP.md`, `ON_MAINTAIN.md`,
  `ON_CONFIGURE.md`: the project's rules, shared with everyone.
  Whatever a file says outside HTML comments is added to the instructions the
  agent receives each time that command runs.
- `ON_PROMPT.local.md` and the like, one per command, only if the user wants
  one: this user's own rules, added after the project's for that command. Like
  every `*.local.md` file in this folder, they are gitignored.

What the script found is listed under Detected State and Current Rules below.

## How to ask

Ask one question at a time, as a menu. Use your question tool if you have one
(in Claude Code, `AskUserQuestion`); otherwise print the options as a numbered
list and wait for the answer. Put the recommended option first and mark it.
When the files already answer a question, that answer is the recommended
option. Every question also accepts an answer the user types.

If `{settings}` already exists, begin by asking what the user wants to do: go
through the questions again, change one thing (ask which), or only check that
everything is in order (go to Finish). Do only what they pick. Do not ask if
the user instruction at the end of this output already says.

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
6. **A note for the agent.** "Which instructions file does your agent read?"
   Options: `CLAUDE.md` (Claude Code), `AGENTS.md` (most other agents), or
   neither. Detected State says which exist and mention `{cdb}/`; recommend
   that one. Add the text of `{agents_snippet}` to the chosen file, creating it
   if needed, and replace any context-db note already there. If the answer to
   question 5 was "also on its own", its sentence becomes: "Read `{cdb}/` when
   a task needs this project's conventions or decisions, starting with
   `{toc_cmd} <folder>` on the project folder." Add nothing else.
7. **When the agent writes to it.** "After `/context-db prompt`, may the agent
   update the knowledge base as it works?" Options: yes, as it goes
   (recommended: what was learned is written down while it is fresh); only when
   you run `/context-db update`. `ON_PROMPT.md` holds a paragraph about this.
   Make it say the answer, replacing the one that is there:
   - As it goes: "You may update the knowledge base as you work, without being
     asked, when you learn something the next agent would get wrong without it:
     a correction from the user, a decision and its reason, a pitfall, a note
     that turned out to be wrong. Run `{update_cmd} '<what you learned>'` and
     follow what it prints. Keep the bar high, tell the user in one line each
     time, and never commit on your own."
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
9. **Cleaning up.** "When it is not obvious how much of the knowledge base
   to clean up after a task, should the agent ask you?" Options: ask
   (recommended; it does this with no rule); clean up without asking;
   delete nothing without asking. Remove any sentence about this from
   `ON_UPDATE.md`, and for the second or third answer add its sentence:
   - Without asking: "Clean up without asking: fix or delete every note you
     judge wrong or no longer needed, and list what you deleted."
   - Nothing without asking: "Delete no note without asking the user first."
10. **Other repositories.** "Does this project rely on other repositories?"
    Options: no, or yes. For each one, get where it is (a path on disk or a URL)
    and one line on what this project uses it for. Record them in `ON_PROMPT.md`
    under the line "Related repositories:", one per line: name, location, what it
    is for. Replace that list if it is already there. Do not clone anything. If a
    repository is on disk and keeps a usage folder, which is what it writes for
    the agents of projects that use it, also offer to mount that folder: a
    symlink at the top level of `{cdb}/`, named after the folder it points to.
    The folder is `context-db/<its name>-project/<its name>-usage/` there,
    unless the `usage_folders` line in its
    `context-db/configuration/settings.md` names other places. If it keeps
    several, offer the one whose description fits what this project uses it
    for. Do not mount its project folder, which is for agents working on that
    project. A mount that is only for this user also goes in `.gitignore`.
11. **Global context.** Global context is knowledge kept outside `{cdb}/`,
    most often the usage folders of other projects. `prompt` finds those
    folders with glob patterns and lists them after this project's own;
    nothing is mounted or copied. Detected State says whether a pattern is set
    and what it matches. Ask: "Should `prompt` also list knowledge folders
    that are kept outside `{cdb}/`?" Options: no (recommended, unless a
    pattern is already set); yes. For yes, get the patterns. Each is read from
    the top of this repository and matches the folders themselves:
    `../*/context-db/*-project/*-usage` matches the usage folder of every
    repository next to this one that keeps it in the usual place, and
    `../*/okf/*-usage` matches every folder whose name ends in `-usage` inside
    the `okf/` folder of each of them. Then run this, with each pattern in
    single quotes after a `--global-context` of its own:

        {setup_cmd} --global-context '<pattern>'

    For patterns that fit only this user's machine, pass
    `--local 'global_context=<pattern>'` for each in place of
    `--global-context`.
12. **Usage folders.** A usage folder holds usage knowledge: what agents in
    other projects need to know to use this one. `/context-db update` writes
    it, and those projects mount it or find it as global context.
    Detected State says where this project's are kept and whether they exist
    yet. Ask only when the user said in question 4 that other code depends on
    this project, or when Detected State shows a `usage_folders` setting:
    "Where should the notes for projects that use this one be kept?" Options:
    inside the project folder, as `{cdb}/<name>-project/<name>-usage/`
    (recommended, unless another place is already set); in a folder of its own
    outside `{cdb}/`, such as `okf/<name>-usage`. For a folder of its own, get
    its path from the top of this repository and run:

        {setup_cmd} --usage-folder <path>

    A project whose users fall into separate groups can keep a usage folder
    for each: pass `--usage-folder` once for each path. For inside the project
    folder, delete the `usage_folders` line from `{settings}` if it has one.
    If a usage folder already exists in the old place, move it to the new
    one. Create each one that does not exist yet with only its descriptor,
    `<folder>/<folder name>.md`: frontmatter with `type: Folder` and a
    `description` that says what this project is. `/context-db update` fills
    it.
13. **Anything else.** Tell the user in a sentence per file what the ON files
    make the agent do now. Then ask: "Is there anything else the agent should
    always do?" Options: no (recommended); yes, for `prompt` (while it works),
    `update` (what gets written down, how commits are made), `wip` (how work in
    progress is kept), or `maintain` (how the knowledge base is tidied). Ask
    them to say it in their own words.

The questions above write the project's rules, which everyone on the project
gets. When an answer is this user's own preference and not the project's, put
it in that command's `.local.md` file instead, creating the file if needed. Ask
when you cannot tell which the user means.

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
  note in `AGENTS.md` or `CLAUDE.md`. Rules of their own go in
  `ON_<COMMAND>.local.md` files there, which are gitignored. They are plain Markdown, and there is
  nothing else to keep in step.
- **What to type**: `/context-db prompt` before work, with the task on a new
  line after it; `/context-db update` after the work. `/context-db wip` is
  optional, for keeping track of long-running work. `/context-db maintain`,
  rarely, tidies the whole knowledge base. `/context-db --help` lists them.
  Each is a starting point: anything else the user wants, they say in words.

Do not commit; leave the changes for the user to review.
