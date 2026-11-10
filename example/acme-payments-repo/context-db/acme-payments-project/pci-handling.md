---
type: Rule
description:
  PCI rules for card data — what may never be stored or logged (card numbers,
  CVV), where tokenization happens, and what needs a security review before it
  merges
---

# PCI handling

This service is in PCI scope. None of these rules can be read off the code.

- Never store or log a full card number or a CVV. Not in the database, not in a
  log line, not in an error message, and not in a queue message.
- Card data is tokenized at the API gateway. The payment engine and the ledger
  only ever see the token.
- Redact a request or a queue message before logging it. Never log a payload as
  it arrived.
- A new column or field that could hold card data needs a review by the
  security team before it merges.
