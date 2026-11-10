---
type: Reference
description:
  The REST API — bearer-token authentication and the payments and refunds
  endpoints
---

# API Reference

## Authentication

Bearer token via `Authorization` header. Tokens issued by `/auth/token`.

## Key Endpoints

- `POST /payments` — initiate a payment
- `GET /payments/:id` — payment status
- `POST /refunds` — initiate a refund
