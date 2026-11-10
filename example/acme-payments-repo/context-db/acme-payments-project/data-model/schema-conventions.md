---
type: Convention
description:
  Table conventions — snake_case names, UUID primary keys, UTC timestamps, soft
  deletes, and which columns get indexes
---

# Schema Conventions

- All tables use `snake_case` naming
- Primary keys are always `id` (UUID v4)
- Timestamps: `created_at` and `updated_at` on every table (UTC)
- Soft deletes via `deleted_at` — no hard deletes in production
- Indexes on all foreign keys and commonly filtered columns
