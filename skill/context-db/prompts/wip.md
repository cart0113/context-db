# context-db Wip

Record where the work in progress stands, so that a later session can pick it
up cold, and write nothing else. Follow the user instruction at the end of
this output. With none, record what this session has been working on.

1. Read `{wip_list}`, and the plan for the current work if it already has one.
2. Update that plan, or create one if the work is new. Bring it up to date
   with what this session has established: put in what is new, and take out
   what is done, settled, or no longer true. Once the work is finished, delete
   the plan and its line instead.
3. Update the work's line in `{wip_list}`, or add one. A new line is started
   today, {today}, on `{branch}`.
4. Run:

       {check_cmd}

   and fix anything it reports.
5. Tell the user in a few lines what the plan now says.

Leave the other plans alone; `/context-db wip --maintain` checks them. Do not
start the planned work itself unless the instruction asks for it.
