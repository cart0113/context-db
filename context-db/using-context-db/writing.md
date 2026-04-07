---
description: How to add new documents and folders to the context-db
---

**Every insight dies with the session unless you write it down.** Non-obvious
knowledge — constraints, gotchas, decisions, patterns — belongs in context-db.
Treat updates as a first-class deliverable, not an afterthought.

## File types

- **Documents** — frontmatter + body. The main content files.
- **Folder descriptions** (`<folder-name>.md`) — frontmatter only, no body.
  Registers the folder in the parent's TOC.

## Frontmatter

Every `.md` file requires YAML frontmatter with a `description` field:

```yaml
---
description: One-line summary shown in the TOC
---
```

Optional: `status: draft | stable | deprecated` (default: `stable`).

## Descriptions must be accurate

The `description` is a **complete, precise summary** — not a title. It must let
an agent decide relevance without opening the file. After any change, rewrite
affected descriptions to match current content exactly.

## Adding a subfolder

1. Create the folder.
2. Add `<folder-name>.md` inside it with frontmatter only (description, no
   body).
3. Add document files inside the folder.
4. Run `show_toc.sh` on the parent to verify it appears correctly.
