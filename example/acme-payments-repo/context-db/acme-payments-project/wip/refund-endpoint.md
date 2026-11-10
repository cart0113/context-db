---
type: Plan
description:
  Adding POST /refunds — asynchronous processing through the ledger queue,
  idempotency keys, and the partial-refund rule still to be decided
status: draft
branch: feature/refunds
---

# Refund endpoint

## Goal

Merchants can refund a captured payment, fully or partially, through
`POST /refunds`.

## Approach

- Refunds are queued, never processed inline: all inter-service calls are
  async, per [architecture.md](../architecture.md).
- The request carries an idempotency key, the same scheme as captures.

## Done

- Route and request validation.

## Next

- Queue consumer and ledger entry.
- Webhook on completion.

## Undecided

- Whether several partial refunds may exceed the captured amount by rounding.
