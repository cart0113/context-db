# context-db

This project keeps reference knowledge in `context-db/` — a hierarchical
Markdown knowledge base of architecture, conventions, decisions, and gotchas,
navigated on demand through a small dispatcher.

**Do not read, load, or browse `context-db/` on your own.** It is not background
reading; pulling it into context unprompted wastes tokens and degrades your
answers. Engage with it only when the user explicitly invokes a `/context-db`
command (`prompt`, `update`, `maintain`, `read`) — the command prints exactly
what to do, and you follow that.

> Opt-in: there is no startup hook — nothing fires unless the user invokes a
> command.
