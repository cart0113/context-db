---
description:
  Why status is the only optional frontmatter field, and why other metadata was
  rejected
---

# Optional Frontmatter Fields

## The decision

The only optional frontmatter field is `status` (default when omitted:
`stable`). All other proposed metadata fields were rejected.

Values: `draft`, `stable`, `deprecated`, `experiment`, `work-in-progress`,
`refactor`.

## Why status

The `_drafts/` prefix convention already handles one lifecycle case — hiding
draft content from the TOC. But it only works at the folder level and requires
moving files between folders to change state. A `status` field generalizes this
to individual documents across all lifecycle stages without requiring folder
reorganization.

An agent seeing `[deprecated]` in a TOC entry knows not to trust that document
for current behavior. An agent seeing `[draft]` knows the content is tentative.
An agent seeing `[experiment]` or `[work-in-progress]` knows the content is
active but not finalized. `[refactor]` marks content about in-progress
architectural changes. This changes agent behavior at zero cost — the field is
only surfaced in the TOC when it's not stable.

## Why not other fields

All rejected for the same reasons: duplicate filesystem/git data, or maintenance
burden exceeds benefit.

- **`last-modified` / `date-created`** — derivable from `stat`/`git log`. LLMs
  are unreliable with timestamps, humans forget to update them.
- **`last-reviewed`** — only non-derivable timestamp, but unmaintained
  `last-reviewed` creates false confidence. Worse than no field.
- **`related`** — links break when files move. Use "See also" in the body.
- **`tags`** — requires consistent vocabulary. The description field and folder
  hierarchy already cover discovery.
- **`aliases`** — marginal value when descriptions are well-written.

## Principle

The only metadata worth adding is metadata that (1) cannot be derived from the
filesystem or git, (2) changes agent behavior, and (3) requires minimal
maintenance. `status` meets all three. The others fail at least one.
