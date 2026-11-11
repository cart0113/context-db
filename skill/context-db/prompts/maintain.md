# Context-db Maintain

Tidy the knowledge base in `{project_dir}/`, following the user instruction at
the end of this output. With no instruction, look at the whole project folder.
With a folder or a topic, look only there.

Your main job is to enforce the rule under Context-db Is Not a Mirror of the
Code, below. `update` follows that rule when it writes; `maintain` goes looking
for where it has been broken, because every note that repeats the project is a
copy that will drift.

Check first, change second. A knowledge base that is in good shape needs
nothing. If you find nothing worth changing, say so in one line and stop.

## What to look for

Start with the format check. Run:

    {check_cmd}

It names files that are too long, folders with too many items, broken links,
and missing descriptions. Then run `{toc_cmd}` on each folder in scope, and
open the files whose descriptions suggest a problem.

First, what the project already says. For every note that talks about code,
open the code it is about, comments included, and compare:

- **Repeats the code or its comments.** File layouts, function signatures, CLI
  flags, what a function does, step-by-step walks through code, anything a
  comment already says: delete it, and link to the code instead. Keep only the
  part the code cannot say, such as why it is that way.
- **Belongs in a comment.** A fact about one piece of code is better next to
  that code. List these for the user as suggested comments; do not edit the
  code yourself.
- **Wrong.** Fix what has drifted from the project's assets, especially code.
  A note that says the code does not follow it yet is a requirement, not a
  stale note: leave it.

Then the shape of the knowledge base:

- **Too long.** A file over about 150 lines becomes smaller files, or a
  subfolder of the same name with a descriptor and one file per topic.
- **Too many items.** A folder with more than about 10 items gets subfolders
  that group related files.
- **Duplicated.** Two files on one topic become one.
- **Vague descriptions.** A description that does not say what the file holds,
  or no longer matches it, gets rewritten. It is all an agent sees before
  deciding whether to open the file.
- **Not worth keeping.** Ask of each note: if it were deleted, would the next
  agent make a mistake it does not make now? If not, it goes.

## How to change it

- Delete without asking only what is plainly false or plainly repeats the
  project. For anything else you want to delete, list it and ask the user
  first.
- When you split, move, or rename a file, search `{cdb}/` for links to it and
  fix them.
- Never edit a background folder; it is owned elsewhere. Leave `{wip_dir}/` to
  `/context-db wip`.

## Finish

Run:

    {check_cmd}

and fix what it reports, until it is clean.
Then tell the user in a few lines what you removed because the project already
says it, what you fixed, split, or merged, and which code comments you suggest.
Leave the changes uncommitted unless the user asks you to commit them.
