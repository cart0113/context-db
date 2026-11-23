---
project: context-db
python: python3
main_branch: v0.1
---

<!--
Settings for the context-db skills. Edit them by hand whenever you like.

- project: the project folder is context-db/<project>-project/.
- python: the command that runs the skills' script, Python 3.8 or newer.
- main_branch: the branch that `/context-db wip --maintain` checks the plans
  against.

Three more are optional. Add them as lines of their own:

- usage_folders: where the usage folders are kept, as paths from the top of
  the repository, such as okf/{project}-usage. {project} stands for the
  project name. Left out, there is one: <project>-usage/ inside the project
  folder. A usage folder holds what other projects need to know to use this
  one, and `/context-db update` writes it.
- global_context: glob patterns that match knowledge folders outside
  context-db/, such as ../*/okf/*-usage. They are read from the top of the
  repository. `/context-db prompt` lists the folders they match.
- settings_files: more settings files to read, such as
  ~/.config/context-db/team.md. Each is read after this file and overrides
  it.

Each of the three takes one value on its line, or several as a list:

    global_context:
      - okf/*-usage
      - ../*/okf/*-usage

settings.local.md in this folder, if it exists, is read after those and
overrides any of this for one user. Every *.local.md file in this folder is
gitignored.
-->
