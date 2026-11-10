# Context-db Configure

Set up or repair context-db in this repository. What the script detected is
listed under Detected State below.

1. Settle three values with the user. Propose the suggested ones, and ask only
   where something is ambiguous.
   - `project`: a short name such as `acme-payments`. The project folder is
     `{cdb}/<project>-project/`.
   - `python`: the command that runs this script. It needs Python 3.8 or newer.
   - `main_branch`: the branch that work in progress is compared against.
2. Run:

       {init_cmd} --project <name> --python <command> --main-branch <branch>

   It writes `{cdb}/{config_name}`, creates whatever is missing without
   overwriting anything, and regenerates the index.

   `{config_name}` is committed and shared by everyone. When a value is right
   only for this user, typically an interpreter path on their machine, leave the
   shared value alone and add `--local python=<command>`. That writes
   `{cdb}/{local_config_name}`, which is gitignored and overrides the shared
   value. Ask the user which file a value belongs in when it is not obvious.
3. Fix every error the index step reported. Rewrite the description in the
   project folder's descriptor so that it says what this project is.
4. If the repository's `AGENTS.md` or `CLAUDE.md` does not mention context-db,
   offer to add the snippet in `{agents_snippet}`.
5. Ask whether any background folders should be mounted: shared standards or
   reference knowledge from another repository. Mount each as a symlink or a
   copy at the top level of `{cdb}/`. They are read-only here.
6. Tell the user what was created and what the config now says.
