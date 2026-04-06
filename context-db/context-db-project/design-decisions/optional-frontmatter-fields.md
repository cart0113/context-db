---
description:
  Why status is the only optional frontmatter field, and why other metadata was
  rejected
---

# Optional Frontmatter Fields

## The decision

The only optional frontmatter field is `status` (values: `draft`, `stable`,
`deprecated`; default when omitted: `stable`). All other proposed metadata
fields were rejected.

## Why status

The `_drafts/` prefix convention already handles one lifecycle case — hiding
draft content from the TOC. But it only works at the folder level and requires
moving files between folders to change state. A `status` field generalizes this
to individual documents across all lifecycle stages without requiring folder
reorganization.

An agent seeing `[deprecated]` in a TOC entry knows not to trust that document
for current behavior. An agent seeing `[draft]` knows the content is tentative.
This changes agent behavior at zero cost — the field is only surfaced in the TOC
when it's not stable.

## Why not other fields

Several other frontmatter fields were considered and rejected for the same
reason: they either duplicate information available from the filesystem/git, or
they add maintenance burden that outweighs the benefit.

**`last-modified` / `date-created`** — Derivable from file modification time
(`stat`) and git history (`git log --follow --diff-filter=A`). Putting
timestamps in frontmatter means they drift — LLMs are unreliable with timestamps
and humans forget to update them. If timestamps are needed in the TOC,
`show_toc.sh` can compute them at runtime from the filesystem.

**`last-reviewed`** — The only non-derivable timestamp (when a human last
verified accuracy against the codebase). But an unmaintained `last-reviewed`
field is worse than no field at all — it creates a false confidence signal. The
maintenance discipline required outweighs the benefit.

**`related` (list of paths)** — Cross-folder relationships between documents.
Useful in theory, but adds a maintenance burden (links break when files move)
and bloats the instructions agents must read. An agent that needs
cross-references can find them in the document body.

**`tags`** — Secondary categorization orthogonal to folder hierarchy. Requires
consistent vocabulary to be useful, adds another axis agents must parse, and the
folder hierarchy already provides the primary organizational axis.

**`aliases`** — Alternative names for discovery. Marginal value when
descriptions are well-written, since a good description naturally includes the
key terms an agent would search for.

## Principle

The only metadata worth adding is metadata that (1) cannot be derived from the
filesystem or git, (2) changes agent behavior, and (3) requires minimal
maintenance. `status` meets all three. The others fail at least one.
