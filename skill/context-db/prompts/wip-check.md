# How to Check the Plans

Read `{wip_list}` and every plan it links to. Also look for files and folders
in `{wip_dir}/` that the list does not mention. Judge each plan by the code
and by git, not by what you remember. Start from the Git State section below.

Work has landed when it is merged into `{main}`, or committed, if you are
working on `{main}` itself. Work that is finished on another branch but not yet
merged has not landed.

- A plan whose work has all landed is finished, whichever branch it names:
  delete it and its line. If only some of it has landed, delete those parts.
  Before deleting, check whether it holds a decision or pitfall a future
  agent will still need once the work is forgotten. If so, move that into the
  main tree of `{project_dir}/` first. Apply the usual bar: only what the
  next agent would get wrong without it.
- A plan whose work has not landed stays, even when a step is done. Record
  the step as done in a line, cut its detail, and update the status on the
  plan's line in the list.
- A plan for a different branch, for a branch that no longer exists, or one
  whose state you cannot judge from the evidence, stays. Ask the user whether
  its work was merged, was dropped, or is still going.
- A plan the list does not mention gets a line, or is deleted if it is
  finished.
