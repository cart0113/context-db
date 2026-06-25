# context-db

This project keeps its knowledge in `context-db/` — a hierarchical Markdown
knowledge base of architecture, conventions, decisions, and gotchas. A small
Python dispatcher exposes it as a set of commands.

Use it like this:

- **Before working on a task**, consult the knowledge base:

  ```bash
  python3 .claude/skills/context-db/scripts/context-db-main-agent.py prompt "<what you're about to do>"
  ```

  It prints how to navigate `context-db/` (a TOC script) and the conventions
  that apply. Follow what it prints, then verify against the actual code.

- **After learning something the next agent would get wrong without it**, file
  it:

  ```bash
  python3 .claude/skills/context-db/scripts/context-db-main-agent.py update "<what was learned>"
  ```

- **To read a whole area** exhaustively:

  ```bash
  python3 .claude/skills/context-db/scripts/context-db-main-agent.py read context-db/acme-payments-project/
  ```

Run `... context-db-main-agent.py help` for the full command list.

> This file is opt-in. There is no startup hook — nothing fires unless you ask.
