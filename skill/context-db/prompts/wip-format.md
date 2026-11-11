# How Work In Progress Is Kept

`{wip_list}` is the list of everything in progress, and `/context-db prompt`
shows it on every run. Keep it short: one line per effort, in this form, and
nothing else.

    - [Refund endpoint](refund-endpoint.md). Started 2026-11-02 on `feature/refunds`. Endpoint done, idempotency next.

- The link goes to the effort's plan, relative to `{wip_dir}/`. Most efforts
  need one file, `<effort>.md`. A large one gets a folder, `<effort>/`, and the
  line links the folder's descriptor, `<effort>/<effort>.md`, which gives the
  overview and links the other files.
- The start date is when the effort began. Never change it.
- After the branch, say in a few words where it stands: what is done, what is
  next, or what it is waiting on.

A plan has `type: Plan`, `status: draft`, and `branch: <branch>` in its
frontmatter. A good plan lets a fresh agent pick the work up cold: the goal, the
approach, what is done, what is next, and what is undecided. Keep the whole plan
current, and do not append a history. A plan follows the same rule as every
note: link to the code it is about, and do not describe what the code already
shows.
