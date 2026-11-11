# Context-db Wip

`/context-db wip` keeps a short record of the work in progress, so that a later
session can pick it up cold. It is optional: a project that does not use it
loses nothing. Your job now is to record the current work, following the user
instruction at the end of this output. With no instruction, record what this
session has been working on.

1. Read `{wip_list}`, and the plan for the current work if it already has one.
2. Update that plan, or create one if the work is new. Put in it what this
   session has established about the work.
3. Update the work's line in `{wip_list}`, or add one. A new line is started
   today, {today}, on `{branch}`.
4. Run:

       {check_cmd}

   and fix anything it reports.
5. Tell the user in a few lines what the plan now says.

Leave the other efforts alone; `/context-db wip --cleanup` deals with them. Do
not start the planned work itself unless the instruction asks for it. Leave the
changes uncommitted unless the user asks you to commit them.
