---
description: REST API endpoints, authentication, and error codes
---

# API Reference

## Authentication

Bearer token via `Authorization` header. Tokens issued by `/auth/token`.

## Key Endpoints

- `POST /payments` — initiate a payment
- `GET /payments/:id` — payment status
- `POST /refunds` — initiate a refund
