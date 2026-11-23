---
type: Convention
description:
  What the owner requires of the docs pages and the README — OKF up front, the
  install prompt first, one-word Title Case navigation, no Why or migration
  page, no logo, no call-to-action buttons, light mode, a restrained look, and
  a Benefits section that is not to be rewritten.
---

# What the owner requires of the docs

- The head of the home page and of the README must say that context-db is built
  on the Open Knowledge Format.
- Early on both, there must be a link to the explainer page,
  [docs/okf.md](../../../docs/okf.md). That page covers what OKF is, a short
  history with a hyperlink for every entry, and which parts context-db uses.
- Both must say plainly that context-db is a set of skills.
- The theme should be colorful, "a bit snazzier than usual". Pages open in
  light mode; the owner asked for "white docs".

Added by the owner on 2026-11-11:

- The home page, the README, and the Setup page lead with the prompt a user
  pastes into their agent to install context-db from the GitHub repository.
  People must be able to point their agent at the repository and have it do the
  setup.
- Labels in the top navigation are Title Case, and one word where possible.
  "Get started" and "Knowledge base" were rejected; they became Setup and
  Layout.
- There is no page for "why" and none for migrating from v0.0. The why is a
  short section, Motivation, at the end of the home page and the README. The
  owner said what goes in it on 2026-11-23: "context information is needed
  for large projects and context-db provides a system to manage large
  context, improving on large linear AGENTS.md file that have to be in every
  time." It ends on what the owner asked for the same day: `update` and
  `maintain` "help guide the agent to create concise, hierarchical
  information that does not duplicate information that can be found by
  reading the code, docs or other project assets". The reasoning about what a
  note costs, and why agents write too much, stays on the Commands page under
  the rule every command repeats.
  Migration is the owner's own task; its guide stays in this knowledge base
  and out of the docs.
- On the Commands page, each command's section is headed by the full command,
  such as `/context-db update`.
- The home page and the README open with the owner's own sentence, which
  names the two kinds of knowledge (2026-11-23): "context-db helps you manage
  project context knowledge needed for development and maintenance", and a
  framework for "usage information: the knowledge other projects need to
  consume to navigate and use your project." The lead is that sentence,
  tightened because the owner wanted "project" used less often in it. Keep it
  close to those words. The agent's own version ended "to understand and use
  yours", and the owner did not like how it ended.
  [voice.md](./voice.md) says why it reads usage information.
- The Example of `prompt` and `update` comes straight after the lead: "The
  example is useful closer to the top." It ends with a steered `update` typed
  over several lines, which [voice.md](./voice.md) explains. It is static; the
  owner asked for "not animated".
- Then "a bit more", under Two kinds of knowledge, in a few plain sentences
  with no table: what project knowledge holds, the owner's sentence on usage
  knowledge ([usage-folders.md](../design-decisions/usage-folders.md)), how a
  project reads another project's usage folder, and that its own knowledge
  comes first. The rest is on the Layout page. What the owner said of the
  longer opening this replaced is in [voice.md](./voice.md).
- Sharing is a section of the Layout page, not a page of its own.
- The Setup page says where the knowledge is before it explains the settings
  (2026-11-23): "By default, it looks for knowledge in the context-db folder",
  then the `<name>-project` folder and "external knowledge folder either
  copied or symlinked into place", then "a section on grabbing information
  from other locations", then a settings section that makes it "clearer what's
  in the setting file" and stays concise. The owner called the Layout page
  "good, could be more concise".
- No logo in the header. The name there and the home page title both read
  `/context-db`.
- No call-to-action buttons under the intro. The owner found the two pill
  buttons "really tired, very much what agents look like". The intro's own link
  to the OKF page and the Install section do that job.
- The footer keeps the theme's Sphinx and PyData credits and nothing else, on
  one small line. The owner had the copyright line removed and the footer
  halved because it "looks really bad on a phone". Check a footer change at
  phone width.
- The Commands page ends with "How it all fits together": what the script
  sends for each command, section by section, next to the ON files. The owner
  wants it "crystal clear how the whole system works", and wants this stressed:
  context-db "is nothing more than some canned context alongside user
  controlled context in the ON files", sent on demand when the user invokes a
  command.
- The home page and the README have a Benefits section after Example, which
  links to that section. The owner wrote its wording by hand on 2026-11-11,
  after rejecting a long list and then a list of one-liners: two or three plain
  sentences a bullet. Fix typos there, but do not rewrite it.
- The commands section of both opens with the API block, and the note that a
  command is a starting point. Neither page mentions `--commit` or `--push`.
  See [command-set.md](../design-decisions/command-set.md).
- Colorful, but restrained. The owner had every gradient halved, the home page
  title cut down, and all type set 10% smaller, because the defaults read "a
  little big". The name in the header was already the right size. Lean smaller
  and quieter when adding to the look.
- context-db works in any agent that runs skills, not only Claude Code. The
  owner (2026-11-23): "careful not to make this look like it only works with
  claude code", naming Codex, T3, and Antigravity, and "I do not want a lot
  about this." Examples may use `.claude/skills/`; say once where it appears
  that other agents use their own folder, such as `.codex/skills/`. Nothing
  in the script or `SKILL.md` may assume `.claude/`.

Follow [voice.md](./voice.md) for every page.
