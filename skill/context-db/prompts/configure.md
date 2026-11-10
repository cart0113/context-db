# Context-db Configure

Set up or repair context-db in this repository. What the script detected is
listed under Detected State below.

1. Tell the user the three values you intend to use. A value that a settings
   file already has stays as it is unless the user asks for a change. For a
   value that is missing, take the suggested one. If that suggestion is marked
   as a guess, or the user has said something that conflicts with it, ask before
   going on. Otherwise go on without waiting.
   - `project`: a short name such as `acme-payments`. The project folder is
     `{cdb}/<project>-project/`.
   - `python`: the command that runs this script. It needs Python 3.8 or newer.
   - `main_branch`: the branch that work in progress is compared against.
2. Run:

       {init_cmd} --project <name> --python <command> --main-branch <branch>

   It writes `{cdb}/{config_name}`, creates whatever is missing without
   overwriting anything, and regenerates the index.

   `{config_name}` is shared by everyone who works on the repository. When a
   value is right only for this user, typically an interpreter path on their
   machine, give the shared file the value that suits the team (usually
   `--python python3`) and add `--local python=<command>`. That writes
   `{cdb}/{local_config_name}`, which is gitignored and overrides the shared
   value. Ask the user which file a value belongs in when it is not obvious.
3. Fix every error that `init` printed.
4. Open the project folder's descriptor, `{cdb}/<project>-project/<project>-project.md`.
   Replace its `description` with one or two specific lines that say what this
   project is. Take them from the README or from what the user has told you.
   Change nothing else in the file.
5. Look for `AGENTS.md` and `CLAUDE.md` at the repository root. If one exists
   and does not mention context-db, offer to append the text of
   `{agents_snippet}` to it. If neither exists, offer to create one from that
   text: `CLAUDE.md` for Claude Code, `AGENTS.md` for most other agents.
6. Ask whether any background folders should be mounted: shared standards or
   reference knowledge from another repository. Mount each one as a symlink or a
   copy at the top level of `{cdb}/`, under the name of the folder it comes
   from. A mount that only this user should have also goes in `.gitignore`.
   Background folders are read-only here.
7. Run:

       {index_cmd} --check

   It must report no errors.
8. Tell the user what was created and what the settings now say. Do not commit;
   leave the new files for the user to review.
