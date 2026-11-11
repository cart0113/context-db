# Context-db Configure

Help the user set up context-db in this repository, or change how it behaves.
There are two things to configure:

- **Settings**, in `{cdb}/{config_name}`: the project name, the Python command,
  the main branch.
- **Rules**, in the four files in `{on_dir}/`. Whatever a file says is added to
  the instructions the agent receives every time its command runs. These files
  are how the user controls what the agent does.

What the script found is listed under Detected State and Current Rules below.

## How to ask

Ask one question at a time, as a menu. Use your question tool if you have one
(in Claude Code, `AskUserQuestion`); otherwise print the options as a numbered
list and wait for the answer. Put the recommended option first and mark it. When
a settings file already has a value, that value is the recommended option. Every
question also accepts an answer the user types.

If the settings file already exists, begin by asking what the user wants to do:
change how the agent behaves (go to Rules), change a setting (go to Settings),
mount a shared folder (question 5), or only check that everything is in order
(go to Finish). Do only what they pick.

## Settings

1. **Project name.** "What should this project be called?" Offer the suggested
   name. The project folder will be `{cdb}/<name>-project/`.
2. **Main branch.** "Which branch is your main branch?" Offer the suggested
   branch. Skip this question when the suggestion is not marked as a guess.
3. **Python.** Ask only when Detected State says `python3` is missing or too
   old: "Which command runs Python 3.8 or newer?" Offer the suggested value, and
   ask whether it is right for the whole team or only for this machine.
4. **Note for the agent.** Look for `AGENTS.md` and `CLAUDE.md` at the
   repository root. If neither mentions context-db: "Add a short note that tells
   the agent not to read the knowledge base unless you ask?" Options: add it to
   the file that exists, create `CLAUDE.md` (Claude Code), create `AGENTS.md`
   (most other agents), or skip. The note is the text of `{agents_snippet}`.
5. **Shared folders.** "Do you want to mount shared knowledge from another
   repository, such as coding standards?" Options: no (recommended), or yes,
   followed by the path. Mount each folder as a symlink at the top level of
   `{cdb}/`, under the name of the folder it comes from. Ask whether the mount is
   for the whole team or only for this user; one that is only for this user also
   goes in `.gitignore`. Shared folders are read-only here.

## Rules

6. **Who updates the knowledge base.** "When should the agent write to the
   knowledge base?"
   - `on-command`: only when you run `/context-db update`. Recommended. Nothing
     is written unless you ask.
   - `agent-decides`: also whenever the agent thinks it has learned something
     worth keeping. It tells you each time, and never commits on its own.
7. **Everything else.** Tell the user, in a sentence or two per command, what
   the rules under Current Rules make the agent do today. Then ask: "Do you want
   to change how the agent behaves?" Options: no, it is fine (recommended when
   the rules are not empty); add or change a rule for `prompt`, the rules the
   agent follows while it works; for `update`, what gets written down and how
   commits are made; for `wip`, how plans are kept.

   For each change, ask the user to say what they want in their own words. Then
   edit the file in `{on_dir}/` yourself:
   - Write the rule as one or two short, direct sentences addressed to the
     agent. Put it outside the HTML comments.
   - Keep each file short. Every line is read on every run. If a rule only
     matters for some tasks, suggest putting it in the knowledge base instead.
   - Leave the paragraph between the "update mode" comments alone; question 6
     manages it.
   - Show the user the file's new text and ask whether it is right. Repeat until
     they have no more changes.

## Then do it

1. Run this with the answers. Leave out any flag whose question you did not ask:

       {init_cmd} --project <name> --update-mode <mode> --main-branch <branch> --python <command>

   For a Python that is right only on this machine, pass `--python python3` and
   add `--local python=<command>`; that goes in `{cdb}/{local_config_name}`,
   which is gitignored and overrides the shared file.

   The command writes the settings, creates whatever is missing without
   overwriting anything, writes the answer to question 6 into
   `{on_dir}/ON_PROMPT.md`, and regenerates the index. On a first setup, run it
   before question 7, so that the rule files exist to be edited.
2. Fix every error it printed.
3. On a first setup, open the project folder's descriptor,
   `{cdb}/<name>-project/<name>-project.md`. Replace its `description` with one
   or two specific lines that say what this project is, taken from the README or
   from what the user has told you. Change nothing else in the file.

## Finish

Run:

    {index_cmd} --check

It must report no errors. Then show the user a short summary: the settings, the
rules as they now stand, and the two commands they will use,
`/context-db prompt "<task>"` before work and `/context-db update --push` after
it. Do not commit; leave the changes for the user to review.
