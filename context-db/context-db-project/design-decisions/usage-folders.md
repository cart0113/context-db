---
type: Decision
description:
  The two kinds of knowledge, project and usage — what the owner decided about
  usage folders and about how a project reads another project's, and which
  parts were the implementing agent's choice
---

# Project knowledge and usage knowledge

The owner's design (2026-11-20, 2026-11-22). A project keeps two kinds of
knowledge, because they have two readers: what agents working on it need, and
what agents in other projects need in order to use it. The owner likens the
second to docs. It is in the same format as the first "so it can be consumed
easily within a project".

## What the owner decided

- There "could be more than one usage folder".
- No flag writes them (2026-11-23). `update` and `maintain` cover the usage
  folders along with the project folder. See
  [command-set.md](./command-set.md).
- The terms are project knowledge and usage knowledge. See
  [voice.md](../writing-docs/voice.md).
- The README and the docs home page name the two "right at the start", in
  a sentence. See
  [docs-requirements.md](../writing-docs/docs-requirements.md).
- On those two pages usage knowledge is "simply the docs/api of the project,
  expressed in okf format and designed to be consumed by other project using
  context-db (which is not necessary either, it's simply okf format md
  files)" (2026-11-23). The owner found a list of what a usage folder holds,
  followed by a comparison with docs, "too complicated". That sentence is the
  pitch, and the rule has not changed: a usage note never reprints an API or
  the docs. The Layout page joins the two with "your docs and API as those
  agents need them".
- A project reads another's usage knowledge "as easily as it's own internal
  project knowledge", and its own is privileged, "more top of mind". So
  `prompt.md` has the agent list the project folder on every task, and look
  into another project's usage folder when the task involves that project.
  [lessons-learned.md](../lessons-learned.md) has the whole order.

## The implementing agent's choices

The owner was told of each in a summary and did not object.

- `usage_folder` became `usage_folders`, with no alias for the old name.
- The usage rules join `update` and `maintain` only once a usage folder
  exists, which keeps both short in a project that nothing else uses.
- `update` never starts the first usage folder unasked, nor one that settings
  do not name. Other projects will read it, so adding it is the user's
  decision. When asked, it creates the descriptor and runs again to get the
  rules, which prints the message twice, once in a project's life.
- The usage sections say only what differs for a reader outside the project.
  Two things must stay in them, because a trial agent had to guess without
  them: what only the code or its comments say does not count as told to that
  reader, and how to judge "wrong" in a usage folder.
- `configure` offers to mount a related repository's usage folder and never
  its project folder, which nobody outside that project needs.
- The human docs call usage knowledge the project's docs and API, as the owner
  does. The usage prompts do not: to an agent "docs" invites a complete reference, and a usage
  folder holds the bare minimum. This is a judgment, not a trial result.
