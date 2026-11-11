# Context-db Wip Cleanup

Make the record of work in progress true again: delete the plans for work that
has landed, and bring the rest up to date. Follow the user instruction at the
end of this output, if there is one.

Work has landed when it is merged into `{main}`, or committed, if you are
working on `{main}` itself. Work that is finished on another branch but not yet
merged has not landed.

1. Read `{wip_list}` and every plan it links to. Also look for files and
   folders in `{wip_dir}/` that the list does not mention.
2. Compare each plan with the Git State below.
   - A plan whose work has all landed is finished: delete it and its line. If
     only some of it has landed, delete those parts. Before deleting, check
     whether it holds a decision or pitfall a future agent will still need once
     the work is forgotten. If so, move that into the main tree of
     `{project_dir}/` first. Apply the usual bar: only what the next agent would
     get wrong without it.
   - A plan whose work has not landed stays, even when a step is done. Record
     the step as done, and update the status on its line.
   - A plan for a different branch, or one whose state you cannot judge from
     the evidence, stays. Ask the user about it.
   - A plan the list does not mention gets a line, or is deleted if it is
     finished.
3. Run:

       {check_cmd}

   and fix anything it reports.
4. Tell the user in a few lines what you deleted, what you moved into the main
   tree, and what is still in progress. Leave the changes uncommitted unless the
   user asks you to commit them.
