# context-db Maintain

Tidy this project's knowledge base, following the user instruction at the end
of this output if there is one. With none, look at all of it: the project
folder, `{project_dir}/`, with its plans, and the usage folders. With a folder
or a topic, look only there. Take a broad view, whatever this session worked
on.

Your main job is to enforce No Duplication, below: find the notes that repeat
the project. Your second job is Keep context-db Small: cut back what is no
longer needed.

Check first, change second. A knowledge base that is in good shape needs
nothing. If you find nothing worth changing, say so in one line and stop.

## What to look for

Start with the format check. Run:

    {check_cmd}

It names files and descriptions that are too long, folders with too many
items, broken links, and missing descriptions. Then run `{toc_cmd}` on each
folder in scope and read the notes there. For this command, every note in
scope bears on the task. Git History, below, says which notes the code has
moved furthest past: start with those.

First, what the project already says. For every note that talks about code,
open the code it is about, comments included, and compare:

- **Repeats the project.** Whatever the rule below says does not belong: cut
  it, and where the note still has to point at it, link to the code or the
  docs. Keep only the part they cannot say, such as why it is that way. A note
  with nothing left goes.
- **Belongs in a comment.** A fact about one piece of code is better next to
  that code. List these for the user as suggested comments; do not edit the
  code yourself, and leave the note until the comment is there.
- **Wrong.** Fix what has drifted from the project's assets, especially code,
  unless the note says that the code does not follow it yet.

Then, what is not needed, or no longer:

- **Outlived its use.** A note about work that is finished, code that is gone,
  a decision that has been reversed, or a problem that no longer exists. Also
  a note that says when to delete it, once that has happened.
- **Says too much.** Background, the story of how something was found, an
  "update" added below what it corrects. Cut the note down to the fact, the
  rule, the pitfall, and the reason, as they stand now.
- **Duplicated.** Two files on one topic become one. A note that repeats a
  background folder goes, because that folder already says it.
- **Not worth keeping.** Ask of each note: if it were deleted, would the next
  agent make a mistake it does not make now? If not, it goes.

Then the shape, so that an agent can find each note from its description
alone:

- **Too long.** A file over about 150 lines becomes smaller files, or a
  subfolder of the same name with a descriptor and one file per topic.
- **Several topics in one file.** The sign is a description that needs more
  than a line or two to say what the file holds. Split it, one topic to a
  file.
- **Too many items.** A folder with more than about 10 items gets subfolders
  that group related files.
- **Vague descriptions.** A description that does not say what the file holds,
  or no longer matches it, gets rewritten. It is all an agent sees before
  deciding whether to open the file.

Last, the plans in `{wip_dir}/`, if How to Check the Plans appears below. That
section, and not the rules here, decides what happens to a plan.
`/context-db wip --maintain` does this part alone.

And the usage folders, if How to Check the Usage Folders appears below. They
have a different reader, and that section says what changes for them.

## How to change it

- Delete a note without asking only when it is plainly false, when it plainly
  repeats the project or a background folder, or when its own first line says
  to delete it and the project shows that the time has come. For any other
  note you want to delete, list it and ask the user first. Cutting a note down
  is not deleting it.
- When you split, move, or rename a file, search `{cdb}/` for links to it and
  fix them.
- Never edit a background folder; it is owned elsewhere.

## Finish

Run:

    {check_cmd}

and fix what it reports, until it is clean. Then tell the user in a few lines
what you removed, and whether that was because the project already says it or
because it is no longer needed, what you fixed, split, or merged, and which
code comments you suggest. Leave the changes uncommitted unless the user asks
you to commit them.
