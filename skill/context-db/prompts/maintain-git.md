# Git History

You were asked to use the git history to find what has gone out of date. Below
is every note in the project folder, the ones the code has moved furthest past
first: when the note last changed, and how many commits have changed the
project outside `{cdb}/` since then. A note that links to project files also
lists which of them changed after the note did.

- Start at the top, and with notes whose linked files changed. For each, see
  what changed since the note did, with `git log --oneline <hash>..HEAD --
  <path>` and `git diff <hash>..HEAD -- <path>`, and check the note against it.
- Look for names the note mentions, such as files, functions, flags, and
  services, that have been renamed or removed since.
- Age alone proves nothing. A decision made a year ago can still hold. Change
  only what the history and the code show to be out of date.
