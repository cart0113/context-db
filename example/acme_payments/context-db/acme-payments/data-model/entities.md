---
description: Core entities — payments, refunds, and merchants
---

# Entities

## Payment

- `id` (UUID) — unique payment identifier
- `amount` (decimal) — payment amount in minor units
- `currency` (string) — ISO 4217 currency code
- `status` (enum) — `pending`, `authorized`, `captured`, `failed`
- `merchant_id` (UUID) — FK to merchant

## Refund

- `id` (UUID) — unique refund identifier
- `payment_id` (UUID) — FK to payment
- `amount` (decimal) — refund amount (partial or full)
- `reason` (string) — refund reason code

## Merchant

- `id` (UUID) — unique merchant identifier
- `name` (string) — display name
- `settlement_account` (string) — bank account for payouts
