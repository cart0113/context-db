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
approach, what is done, what is next, and what is undecided. It is opened at
the start of every session on that work, so it holds what that agent needs in
order to go on, and nothing else. Keep the whole plan current, and do not
append a history. Say what is done in a line and cut the detail, because the
code and the git log hold it. A plan follows the same rule as every note: link
to the code it is about, and do not describe what the code already shows.

## Feature branches

A useful pattern is one feature branch for each effort, with its plan and its
line kept on that branch, so that the list there is about that work. Once the
branch is merged, `{main}` must not list the effort: delete the plan and its
line before the merge, or on `{main}` straight after it.
