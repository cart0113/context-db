# TOC File Format

`<folder>_toc.md` files are fully generated. Never edit them.

## Example

From the acme_payments example (`acme_payments_toc.md`):

```markdown
## Subfolders

- description: Database schema, entities, and relationships
  path: data_model/data_model_toc.md

## Files

- description: REST API endpoints, authentication, and error codes
  path: api_reference.md
- description: System components, data flow, and service boundaries
  path: architecture.md
```

Each entry has `description:` on the first line and `path:` on the second.

## Sections

Sections only appear when there are entries — an empty folder produces an empty TOC.

| Section    | Contents                                                          |
|------------|-------------------------------------------------------------------|
| Subfolders | Subdirectories that have a description file                       |
| Files      | `.md` files (excluding the description file and the `_toc.md`)    |

Underscore-prefixed and dot-prefixed names are excluded.
