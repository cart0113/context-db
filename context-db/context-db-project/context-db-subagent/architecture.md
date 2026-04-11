---
description:
  Subagent architecture — single script with four modes, instructions mode
  generates config-aware directives, model navigates the B-tree, content-first
  prompt ordering
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

## Instructions mode

The main agent needs to know when to call ask/review/maintain, what command to
run, and what the response means. The `instructions` mode reads config and
stitches together directive language:

- Exact commands with the script's resolved path
- What each response is and who it's from (project knowledge expert)
- Mandatory vs optional (automatic = "You MUST", confirm = "Ask the user")
- Frequency rules for ask mode (always, new topic, major only)
- Skipped modes are omitted entirely

The rule and hook both call `context-db-agent.py instructions`. The main agent
follows the output. Config changes take effect on next session start.

## Why the model must navigate

Early versions had Python read all context-db files and stuff them into the
system prompt. This broke the fundamental design: the B-tree exists so the model
makes smart routing decisions based on descriptions. Python can't judge which
folders are relevant to a prompt — that's a language understanding task.

The model reads descriptions at each level, drills into relevant folders, skips
irrelevant ones. This scales with large knowledge bases and works correctly with
cross-project symlinks (the TOC script handles those).

## Content-first prompt ordering

The user message puts the content before the navigation instructions:

```
Developer's prompt: commit everything to git

Now navigate the project knowledge base to find relevant conventions...
Use the TOC script to browse: ...
```

The model reads what it needs to find context FOR, then goes looking. This
produces better results than instructions-first ordering because the model knows
what to filter for before it starts navigating.

## Two-prompt structure

- **System prompt:** Role only — what kind of response to produce (bullet points
  for ask, violations for review, filing recommendation for maintain)
- **User message:** The content to process + how to navigate context-db

This separation keeps the role stable across the session while the content
varies per call.

## Environment guard

The script sets `CONTEXT_DB_SUBAGENT=1` in the environment before calling
`claude -p`. The session-start hook checks this and exits early — prevents the
subagent from receiving its own instructions recursively.
