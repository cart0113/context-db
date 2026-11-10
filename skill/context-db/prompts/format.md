# File Format

Every `.md` file in the knowledge base starts with YAML frontmatter:

    ---
    type: Decision
    description:
      Why refunds are processed asynchronously, and the idempotency-key rule that
      follows from it
    ---

- `type` is required. It says what kind of knowledge the file holds, and the
  Open Knowledge Format requires it. Use one of `Decision`, `Convention`,
  `Rule`, `Architecture`, `Gotcha`, `Reference`, `Research`, `Plan`, or
  `Folder`. A `Rule` is a requirement imposed on the project, such as a business
  or compliance rule; a `Convention` is how the team chooses to do things. Coin
  a new type only when none fits.
- `description` is required. It is the only thing an agent sees before deciding
  whether to open the file, so be specific: "scheduler execution flow, budget
  enforcement hook", not "Architecture overview". Include alternative terms when
  a topic goes by several names.
- `status` is optional: `draft` or `deprecated`. Omit it when the content is
  stable.
- Add no other keys, except `branch` on files in `wip/`.

The frontmatter must be valid YAML. In a description, do not write a colon
followed by a space, or a space followed by `#`, and do not start it with a
quote, a backtick, or a bracket. If you need any of those, wrap the whole
description in double quotes.

**Folders.** Every folder has a descriptor named after it,
`<folder>/<folder>.md`, with `type: Folder` and a description of what the folder
holds. A body is optional. Aim for 5–10 items per folder.

**Index files.** `index.md` is generated from frontmatter. Never write or edit
one.

**Links.** Use real Markdown links, relative to the file that contains them:
`[retry policy](./retry-policy.md)`, `[the dispatcher](../../src/dispatch.py)`.
Never start a link with `/`.

**Size.** About 150 lines per file, 200 at most. Split a larger file into a
subfolder of the same name. Files in `wip/` are exempt.

**Style.** State the fact, the convention, the pitfall. No exposition, and no
justification unless the reason is the point. If a file reads like
documentation, it is too long.
