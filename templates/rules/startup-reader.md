This project uses a `context-db/` knowledge base — a hierarchical Markdown
repository of conventions, standards, design decisions, and pitfalls.

On your first response to the user, or when the topic shifts significantly, run:

    /context-db prompt "<user's request>"

This searches context-db for standards, conventions, and pitfalls relevant to
the task. Use what it returns to inform your work.

Context-db is a starting point — a map, not truth. It documents things you can't
learn from reading any single file. Use it to orient yourself, then verify
against actual project assets (code, configs, docs). If what you find conflicts
with the project, trust the project.

For detailed instructions on any capability: `/context-db load-manual <section>`
