<!--
Everything in this file outside HTML comments is added to every
`/context-db prompt`, immediately before the user's instruction. Edit it by hand
whenever you like.

Keep it to the few rules the agent must see every time: every line is read on
every run. An empty file adds nothing.
-->

This is a payments service and it is PCI-scoped. Before touching anything that
handles card data, storage, or logging, read
`context-db/acme-payments-project/pci-handling.md`. Do not infer the rules from
the code alone.

Write to the knowledge base only when the user runs `/context-db update`. At
any other time, leave `context-db/` alone. If you learn something worth keeping, say
so in one line and suggest that command.
