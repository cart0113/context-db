# Context-db Update

Decide first whether there is anything to store. Think back over this session:
corrections the user made, conventions you learned, pitfalls you hit, decisions
and the reasons for them. Would the next agent get something wrong, or miss
something, without it? If not, {nothing_to_add}.

Most sessions produce nothing worth storing. That is the normal outcome, not a
failure. Every addition dilutes what is already there.

## What belongs

Things the next agent would get wrong or miss: conventions, corrections from the
user, pitfalls, design rationale, domain knowledge.

What does not belong: anything derivable from the project's assets (code,
configs, docs). No file layouts, function signatures, CLI flags, or step-by-step
restatements of code. Link to code and docs; never restate them.

## Where it goes

Write only inside `{project_dir}/`. Every other folder under `{cdb}/` is a
background bundle owned elsewhere: never edit one.

Read `{project_dir}/index.md` and navigate to see what is already documented.
Update an existing file when it covers the topic. Create a file only for a
genuinely new topic. Delete content that has become false or has drifted into a
summary of the code. A smaller, accurate bundle beats a larger one.

Plans and the status of ongoing work do not go in the main tree. They live in
`{project_dir}/wip/`, which `/context-db wip` manages.

The files in `{on_dir}/` are inlined on every matching command, so each line in
them costs tokens every time. Put something there only when it must be seen
every time, and ask the user first.

Context-db is the project's memory. Do not also save this to an auto-memory or
any vendor-specific memory file.

## Finish

Run:

    {index_cmd}

It regenerates every `index.md` and reports format problems. Fix what it reports
and run it again until it is clean. Never edit an `index.md` by hand.

Do not run `/context-db update` yourself; the user invokes it.
