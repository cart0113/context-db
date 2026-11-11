# Context-db Wip Clear

The user wants to clear the record of work in progress: delete every plan in
`{wip_dir}/` and empty the list in `{wip_list}`.

1. Show the user what will be deleted: every file and folder in `{wip_dir}/`
   except `wip.md` and `index.md`. If a plan holds a decision or pitfall a
   future agent will still need, say so and offer to move it into the main tree
   of `{project_dir}/` first. Ask the user to confirm. Stop if they do not.
2. Delete them. In `{wip_list}`, delete every line of the list and keep the
   rest of the file.
3. Run:

       {index_cmd}

   and fix anything it reports.
4. Tell the user what you deleted. Leave the changes uncommitted unless the user
   asks you to commit them.
