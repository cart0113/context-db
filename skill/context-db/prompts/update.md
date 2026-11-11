# Context-db Update

Decide first whether there is anything to store. Think back over this session:
corrections the user made, conventions you learned, pitfalls you hit, decisions
and the reasons for them. Would the next agent get something wrong, or miss
something, without it? If not, {nothing_to_add}.

Most sessions produce nothing worth storing. That is the normal outcome, not a
failure. Every addition dilutes what is already there.

When there is something, change only what it needs: the one or two files the
lesson belongs in. Do not tidy, reword, or reorganize anything else on the way;
that is what `/context-db maintain` is for.

## What belongs

What the next agent would get wrong or miss, and that the project itself does
not say: corrections from the user, conventions, pitfalls, design rationale,
domain knowledge, rules the project must obey. The rule under Context-db Is Not
a Mirror of the Code, below, decides: anything an agent could learn by reading
the code and its comments stays out.

A rule that the code does not follow yet still belongs. Say in the entry that
the code does not enforce it yet, so that the next agent does not take the code
as proof that the entry is wrong.

## Where it goes

Write inside the project folder, `{project_dir}/`. The folders listed under
Folders below as background folders are owned elsewhere: never edit one.

Run `{toc_cmd} {project_dir}` to see what is already documented, and open only
the files whose descriptions suggest they cover the topic. Update an existing
file when it covers the topic. Create a file only for a genuinely new topic.
Delete content that has become false or has drifted into a summary of the code.
A smaller, accurate knowledge base beats a larger one.

Plans and the status of ongoing work do not go in the main tree. If the
project records them, they live in `{wip_dir}/`, which `/context-db wip`
manages.

The one place outside the project folder that you may write to is the ON files
in `{conf_dir}/`. Each is inlined on every run of its command, so each line in
them costs tokens every time. Put something there only when it must be seen
every time, and ask the user first.

Context-db is the project's memory. Do not also save this to an auto-memory or
any vendor-specific memory file.

## Finish

Run:

    {check_cmd}

It checks the format of the whole project folder. Fix what your change caused,
and run it again until that is clean. If it reports problems in files you did
not touch, leave them, and mention them in one line with a suggestion to run
`/context-db maintain`.
