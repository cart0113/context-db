---
okf_version: "0.2"
---

# Subfolders

* [data-model](data-model/index.md) - Database schema — the payment, refund, and merchant entities, and the conventions every table follows
* [wip](wip/index.md) - Current work in progress — plans for what is being built right now. Files here are deleted once the work lands.

# Files

* [API Reference](api-reference.md) - The REST API — bearer-token authentication and the payments and refunds endpoints
* [Architecture](architecture.md) - The three services (API gateway, payment engine, ledger), what each one owns, and the rule that services talk only through the message queue
* [PCI handling](pci-handling.md) - PCI rules for card data — what may never be stored or logged (card numbers, CVV), where tokenization happens, and what needs a security review before it merges
