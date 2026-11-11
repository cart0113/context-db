# Context-db Configure

Set up or repair context-db in this repository by asking the user a short
series of questions, then running one command with the answers. What the script
detected is listed under Detected State below.

## How to ask

Ask one question at a time, as a menu. Use your question tool if you have one
(in Claude Code, `AskUserQuestion`); otherwise print the options as a numbered
list and wait for the answer. Put the recommended option first and mark it. When
a settings file already has a value, that value is the recommended option. Every
question also accepts an answer the user types.

## The questions

1. **Project name.** "What should this project be called?" Offer the suggested
   name. The project folder will be `{cdb}/<name>-project/`.
2. **Who updates the knowledge base.** "When should the agent write to the
   knowledge base?"
   - `on-command`: only when you run `/context-db update`. Recommended. Nothing
     is written unless you ask.
   - `agent-decides`: also whenever the agent thinks it has learned something
     worth keeping. It tells you each time, and never commits on its own.
3. **Main branch.** "Which branch is your main branch?" Offer the suggested
   branch. Skip this question when the suggestion is not marked as a guess.
4. **Python.** Ask only when Detected State says `python3` is missing or too
   old: "Which command runs Python 3.8 or newer?" Offer the suggested value, and
   ask whether it is right for the whole team or only for this machine.
5. **Note for the agent.** Look for `AGENTS.md` and `CLAUDE.md` at the
   repository root. If neither mentions context-db: "Add a short note that tells
   the agent not to read the knowledge base unless you ask?" Options: add it to
   the file that exists, create `CLAUDE.md` (Claude Code), create `AGENTS.md`
   (most other agents), or skip.
6. **Shared folders.** "Do you want to mount shared knowledge from another
   repository, such as coding standards?" Options: no (recommended), or yes,
   followed by the path.

## Then do it

1. Run:

       {init_cmd} --project <name> --update-mode <mode> --main-branch <branch> --python <command>

   Use `--python python3` unless question 4 was asked. For a Python that is
   right only on this machine, keep `--python python3` and add
   `--local python=<command>`; that goes in `{cdb}/{local_config_name}`, which
   is gitignored and overrides the shared `{cdb}/{config_name}`.

   The command writes the settings, creates whatever is missing without
   overwriting anything, writes the answer to question 2 into
   `{cdb}/context-db-on-markdown/ON_PROMPT.md`, and regenerates the index.
2. Fix every error it printed.
3. Open the project folder's descriptor,
   `{cdb}/<name>-project/<name>-project.md`. Replace its `description` with one
   or two specific lines that say what this project is, taken from the README or
   from what the user has told you. Change nothing else in the file.
4. Carry out the answer to question 5. The note is the text of
   `{agents_snippet}`.
5. Carry out the answer to question 6. Mount each folder as a symlink at the top
   level of `{cdb}/`, under the name of the folder it comes from. Ask whether the
   mount is for the whole team or only for this user; one that is only for this
   user also goes in `.gitignore`. Shared folders are read-only here.
6. Run:

       {index_cmd} --check

   It must report no errors.
7. Show the user a short summary: the settings, what was created, and the two
   commands they will use, `/context-db prompt "<task>"` before work and
   `/context-db update --push` after it. Do not commit; leave the new files for
   the user to review.
