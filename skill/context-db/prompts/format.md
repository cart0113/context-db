# File Format

Every `.md` file in the knowledge base starts with YAML frontmatter:

    ---
    type: Decision
    description:
      Why refunds are processed asynchronously, and the idempotency-key rule that
      follows from it
    ---

- `type` is required. One short label for the kind of knowledge: `Folder`,
  `Decision`, `Convention`, `Architecture`, `Gotcha`, `Reference`, `Research`,
  or `Plan`. Pick the closest; coin a new one only when none fits.
- `description` is required. It is the only thing an agent sees before deciding
  whether to open the file, so be specific: "scheduler execution flow, budget
  enforcement hook", not "Architecture overview". Include alternative terms when
  a topic goes by several names.
- `status` is optional: `draft` or `deprecated`. Omit it when the content is
  stable.
- Add no other keys, except `branch` on files in `wip/`.

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
