<!--
Everything in this file outside HTML comments is inlined on every
`/context-db prompt`, immediately before the user's instruction.
-->

This is a payments service and it is PCI-scoped. Before touching anything that
handles card data, storage, or logging, check the project bundle for the
handling rules. Do not infer them from the code alone.
