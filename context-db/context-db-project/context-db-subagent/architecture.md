---
description:
  Subagent architecture — runs from inside context-db/, stream-json for live
  output, constrained navigation (TOC + Read only), cost tracking
---

# Subagent Architecture

## Single script, four modes

`context-db-agent.py` is the only script. It handles all four modes:

- **instructions** — reads `.contextdb.json`, outputs tailored directives for
  the main agent. Called by the session-start hook and the rule. The main agent
  never sees `.contextdb.json`.
- **ask/review/maintain** — calls `claude -p` with tools so the subagent model
  navigates context-db itself.

The script does NOT read context-db files. The model does.

## Runs from inside context-db/

The subagent runs with `cwd=context-db/` and `--bare` (no hooks, no rules, no
skills, no CLAUDE.md). This sandboxes it to just the markdown files. The model
has no access to project code, git history, or other tools. It sees only the TOC
script (passed as an absolute path) and the files in its working directory.

## Instructions mode

The main agent needs to know when to call ask/review/maintain, what command to
run, and what the response means. The `instructions` mode reads config and
stitches together directive language:

- Exact commands with the script's resolved path.
- What each response is and who it's from (project knowledge expert).
- Mandatory vs optional (automatic = "You MUST", confirm = "Ask the user").
- Wait instruction — main agent must not explore the codebase in parallel.
- Frequency rules for ask mode (always, new topic, major only).
- Skipped modes are omitted entirely.

The rule and hook both call `context-db-agent.py instructions`. The main agent
follows the output. Config changes take effect on next session start.

## Constrained navigation

The system prompt tells the model to navigate using ONLY the TOC script and
Read. No `find`, `grep`, or `ls`. This keeps haiku focused:

1. Run TOC on `.` to see top-level descriptions.
2. Pick relevant folders or files from descriptions.
3. If folder, run TOC on it. If file, read the whole file (~100 lines each).
4. Repeat until done.

This produces clean 2-3 step navigation. Without these constraints, haiku adds
defensive commands (`head -50`, `2>/dev/null`, `find`, `ls -la`) that waste
turns and slow things down.

## Stream-json output

The script uses `--output-format stream-json` with `--verbose` to stream events
as the subagent works. It prints tool calls live (reading/running) so the caller
can see progress, then outputs the final result demarcated:

```
--- context for prompt ---
[subagent's response]
--- end context ---

--- metadata ---
model: haiku | cost: $0.0191 | tokens: 88in/28out | time: 20.6s
--- end metadata ---
```

The demarcation prevents the main agent from confusing metadata with context.

## Environment guard

The script sets `CONTEXT_DB_SUBAGENT=1` in the environment before calling
`claude -p`. The session-start hook checks this and exits early — prevents the
subagent from receiving its own instructions recursively.
