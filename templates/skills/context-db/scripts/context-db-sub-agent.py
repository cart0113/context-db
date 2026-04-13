#!/usr/bin/env python3
"""
context-db-sub-agent.py — spawns claude -p for isolated context-db lookups.

Only called when mode=sub-agent. The main agent calls this based on
instructions from context-db-main-agent.py.

Spawns claude -p with system prompt + user message from prompts/ templates.
Parses stream-json output. Returns [response] + [response-instructions].

Sub-commands (matching context-db-main-agent.py):
  prompt        Consult context-db for knowledge/standards
  pre-review    Check plan against standards before implementing
  review        Review changes against conventions
  update        File learnings into context-db

Usage:
  context-db-sub-agent.py prompt "user instruction"
  context-db-sub-agent.py prompt "user instruction" --model sonnet
  context-db-sub-agent.py review "summary" --review-type full --debug

Dependencies: python3 (stdlib only), claude CLI
"""

# TODO: Implement — Step 5 of unify refactor plan
