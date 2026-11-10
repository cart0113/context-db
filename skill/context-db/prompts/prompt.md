# Context-db Prompt

`{cdb}/` holds this project's knowledge base: conventions, decisions, gotchas,
and current plans that cannot be learned from reading any single project file.
Consult it now, for the user instruction at the end of this output.

## How to navigate

Each bundle listed below is a small wiki. Start at its `index.md`, which has one
line per file and subfolder, each with a description. Then:

- Open a file only when its description says it bears directly on the
  instruction.
- Open a subfolder's `index.md` only when the subfolder's description does.
- Skip everything else. Reading widely dilutes what matters.
- Links inside a file are relative to that file.

`{project_dir}/` is the project bundle: knowledge specific to this repository.
Background bundles are general reference material shared from elsewhere, such as
standards and domain knowledge. Consult them when the instruction touches what
they cover.

## How to use what you find

Context-db is a map, not the territory. Use it to orient, then verify against
the project's assets (code, configs, docs). Where they conflict, trust the
project's assets, especially code, and tell the user what is out of date.

Do not run `/context-db prompt` yourself; the user invokes it. To consult
context-db again later in the session, navigate it the same way.
