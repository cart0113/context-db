# context-db Update

Decide first whether the knowledge base needs to change at all. Think back
over this session, for these things:

- What you learned that the next agent would get wrong, or miss, without it:
  corrections the user made, conventions, pitfalls, decisions and the reasons
  for them.
- What the notes you read turned out to be: one that is out of date, one that
  sent you the wrong way, one that says only what the code shows.
- Whether a plan in `{wip_dir}/` that this session worked from still says
  where the work stands.{usage_thought}

If there is none of these, {nothing_to_add}. Most sessions change nothing,
and that is the normal outcome.

If there is a user instruction at the end of this output, follow it. It may
say what to record, or narrow or widen where you look.

When there is something, change only what it needs: the one or two files the
lesson belongs in, and the notes that turned out wrong or not needed, which
you fix or delete. Do not tidy, reword, or reorganize anything else on the
way; that is what `/context-db maintain` is for. If you came across other
notes that look out of date, repeated, or no longer needed, name them in a
line and ask the user whether to clean them up.

## What belongs

No Duplication, below, decides.

A rule that the code does not follow yet still belongs. Say in the note that
the code does not enforce it yet.

When you know that a note will stop mattering, say when in its first line, as
in "Delete this once the v1 endpoints are gone."

## Where it goes

Write inside the project folder, `{project_dir}/`, which holds project
knowledge: what agents working on this project need. Never edit a background
folder; it is owned elsewhere.

Run `{toc_cmd} {project_dir}` first, to see what is already documented.

Some things have a home of their own, and do not go in the main tree:

- Plans and the status of ongoing work: `{wip_dir}/`. Bring a plan this
  session worked from, and its line in `wip.md`, up to date, and delete both
  once the work is finished. `/context-db wip` handles the other plans.
- Usage knowledge, which is what agents in other projects need to know to use
  this one: {usage_home}
- What must be seen on every run: an ON file in `{conf_dir}/`. Each line
  there costs tokens on every run of its command, so ask the user first.

If you learned something about using a project that this one depends on, it
belongs in that project's own usage folder, which you cannot write. Tell the
user in one line what that folder should say.

context-db is the project's memory. Do not also save this to an auto-memory or
any vendor-specific memory file.

## Finish

Read your change once more as the next agent would, cold, and cut every line
that agent would not miss. Then run:

    {check_cmd}

It checks the format of the project folder, and of each usage folder that is
kept outside it. Fix what your change caused, and run it again until that is
clean. If it reports problems in files you did not touch, leave them, and
mention them in one line with a suggestion to run `/context-db maintain`.

Tell the user in a line or two what you added, changed, and deleted.
