# Context-db Prompt

`{cdb}/` is this project's knowledge base: conventions, decisions, gotchas, and
current plans that cannot be learned from reading any single project file.
Consult it now, for the user instruction at the end of this output.

## How to navigate

Start with the plans listed under Work In Progress below. Then go to the
folders listed under Folders. Each folder is a small wiki: its `index.md` has
one line per file and subfolder, each with a description.

- Open a file only when its description says it bears directly on the
  instruction.
- Open a subfolder's `index.md` only when the subfolder's description does.
- Skip everything else. Reading widely dilutes what matters.
- Links inside a file are relative to that file.

The project folder holds knowledge specific to this repository. Background
folders hold general reference material shared from elsewhere, such as standards
and domain knowledge. The same test applies to them: open what bears directly
on the instruction.

## How to use what you find

Context-db is a map, not the territory. Use it to orient, then verify against
the project's assets (code, configs, docs). Where they conflict, trust the
project's assets, especially code, and tell the user what is out of date. The
exception is an entry that says the code does not follow it yet: that is a
requirement still to be built, not a stale note.

Do not run `/context-db prompt` yourself; the user invokes it. To consult
context-db again later in the session, navigate it the same way.
