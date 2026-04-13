---
description:
  Why the sub-agent uses indirection (instructions mode), environment guard
  rationale, API key stripping rationale. Superseded by unified /context-db
  skill.
status: deprecated
---

# Subagent Architecture — Design Decisions

## Why instructions mode exists

The main agent never reads `.contextdb.json`. Instead, `instructions` mode reads
it and outputs tailored directives. This means:

- Config changes take effect without editing rules or prompts
- The main agent gets exactly the instructions it needs (no parsing, no
  conditionals)
- Different `when` settings produce different instruction text — the main agent
  doesn't need to understand frequency logic

## Why combined workflow

When both pre-review and code-review are enabled, instructions mode outputs a
single numbered sequence (pre-review → make changes → code-review). Without
this, the main agent treats them as independent optional calls and skips
whichever it finds inconvenient. A numbered workflow is harder to skip steps
from.

## API key stripping

The script strips `ANTHROPIC_API_KEY` from the subprocess environment. Without
this, the subagent uses the API key (which may be exhausted or rate-limited)
instead of falling back to Max plan login auth. The `--bare` flag was also
removed because bare mode + no API key = no auth at all.

## Environment guard

`CONTEXT_DB_SUBAGENT=1` is set in the subprocess env. The session-start hook
checks this and exits early — prevents the subagent from receiving its own
instructions recursively.
