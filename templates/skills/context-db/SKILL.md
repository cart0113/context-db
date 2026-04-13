---
name: context-db
description:
  'Project knowledge base — consult conventions and standards, review changes,
  file learnings, audit and maintain.'
allowed-tools: Bash,Read,Write,Edit,Glob,Grep
---

## Usage

Pass your sub-command and instructions to the dispatcher:

```
python3 .claude/skills/context-db/scripts/context-db-main-agent.py <command> [args] [flags]
```

## Commands

### READ — consult the knowledge base

- **prompt** "<instruction>" — Consult context-db for relevant knowledge and
  standards before starting work.
- **pre-review** "<plan>" — Check your plan against standards before
  implementing.
- **review** "<summary>" — Review your changes against project conventions.

### WRITE — update the knowledge base

- **update** "<learnings>" — File learnings from this session into context-db.
- **maintain** [path] — Audit and maintain context-db quality (7-phase).

## Flags

- `--mode sub-agent|main-agent` — Override execution mode
- `--model haiku|sonnet|opus` — Override model for sub-agent mode
- `--review-type context-db|full` — Override review scope (review only)
- `--debug` — Show system prompts and tool calls

## How results come back

The script outputs structured sections. Follow the instructions in each:

- `[response]` — The findings or instructions
- `[response-instructions]` — How to treat the response
- `[reminder]` — Available commands (re-instruction for context rot)
