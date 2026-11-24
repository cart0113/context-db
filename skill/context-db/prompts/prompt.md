# context-db Prompt

`{cdb}/` is this project's knowledge base: conventions, decisions, pitfalls,
and plans that cannot be learned by reading the project. Consult it now, for
the user instruction at the end of this output.

If a Work In Progress section appears below, start with the plans it lists
that bear on the instruction. Then look into the folders listed under Folders,
the way How to Navigate context-db says.

- The project folder holds project knowledge: this project's own, for agents
  working on it. Start there on every task, because it applies to everything
  done in this repository.
- A usage folder holds usage knowledge: what a project tells agents in other
  projects about using it. When the instruction involves a project that this
  one uses, look for that project's usage folder among the background folders
  and under Global Context, and look into it before you read that project's
  code. Look into this project's own usage folder, if Folders lists one, when
  the instruction changes how this project is used.
- A background folder is any other folder in `{cdb}/`, such as shared
  standards or domain knowledge. Global Context, when that section appears
  below, lists knowledge folders that are kept outside `{cdb}/`.

One test applies to every folder: open what bears directly on the
instruction. Verify what you find against the project's assets (code, code
comments, configs, docs), and tell the user what is out of date. Whether you
may write to context-db on your own is stated in the rules near the end of
this output.

Do not run `/context-db prompt` yourself; the user invokes it. To consult
context-db again later in the session, navigate it the same way.
