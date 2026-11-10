# Context-db Wip

`{wip_dir}/` holds the plans for work in progress. It is what centers an agent
on what is being built right now. Your job is to make it true again, following
the user instruction at the end of this output.

Work has landed when it is merged into `{main}`, or committed, if you are
working on `{main}` itself. Work that is finished on another branch but not yet
merged has not landed.

1. Read every file listed under Work In Progress below.
2. Compare each one with the Git State below.
   - A plan whose work has all landed is finished: delete the file. If only some
     of it has landed, delete those parts. Before deleting, check whether it
     holds a decision or pitfall a future agent will still need once the work is
     forgotten. If so, move that into the main tree of `{project_dir}/` first.
     Apply the usual bar: only what the next agent would get wrong without it.
   - A plan whose work has not landed stays, even when a step is done. Record
     the step as done.
   - A file marked for a different branch, or one whose state you cannot judge
     from the evidence, stays. Ask the user about it.
3. Write or update the plan for the current work. One file per effort, named for
   the effort, with `type: Plan`, `status: draft`, and `branch: {branch}` in its
   frontmatter. A good plan lets a fresh agent pick the work up cold: the goal,
   the approach, what is done, what is next, and what is undecided. Include what
   this session has established about the work. Keep the whole file current,
   its description included, because the description is what `/context-db
   prompt` shows. Do not append a history.
4. Run:

       {index_cmd}

   and fix anything it reports.
5. Tell the user in a few lines what you deleted, what you moved into the main
   tree, and what the plan now says. Leave the changes uncommitted unless the
   user asks you to commit them.

With no user instruction, do steps 1 and 2 and summarize what is in progress.

Do not start the planned work itself unless the instruction asks for it. Do not
run `/context-db wip` yourself; the user invokes it.
