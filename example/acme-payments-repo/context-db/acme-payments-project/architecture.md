---
type: Architecture
description:
  The three services (API gateway, payment engine, ledger), what each one owns,
  and the rule that services talk only through the message queue
---

# Architecture

Acme Payments is a three-tier service:

1. **API Gateway** — validates requests, rate limiting, auth
2. **Payment Engine** — orchestrates payment flows, retries, idempotency
3. **Ledger** — append-only transaction log, double-entry bookkeeping

All inter-service communication is async via message queue.
