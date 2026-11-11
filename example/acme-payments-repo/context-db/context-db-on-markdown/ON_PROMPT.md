<!--
Everything in this file outside HTML comments is inlined on every
`/context-db prompt`, immediately before the user's instruction.
-->

This is a payments service and it is PCI-scoped. Before touching anything that
handles card data, storage, or logging, read
`context-db/acme-payments-project/pci-handling.md`. Do not infer the rules from
the code alone.

<!-- context-db update mode: written by configure. Reword it freely. -->
Write to the knowledge base only when the user runs `/context-db update`. At
any other time, leave `context-db/` alone. If you learn something worth keeping, say
so in one line and suggest that command.
<!-- end of context-db update mode -->
