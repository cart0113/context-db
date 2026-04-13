#!/usr/bin/env python3
"""
context-db-main-agent.py — dispatcher for /context-db skill.

Always called by the main agent via SKILL.md. Reads config, determines mode,
and either:
  - Prints instructions for the main agent to follow directly (main-agent mode)
  - Prints instructions telling the main agent to call context-db-sub-agent.py
    (sub-agent mode)
  - Prints instructions to ask the user which mode (ask mode)

Every response includes a [reminder] block with available commands to handle
context rot.

Sub-commands:
  init          Startup instructions (called by rule, not in SKILL.md)
  prompt        Consult context-db for knowledge/standards
  pre-review    Check plan against standards before implementing
  review        Review changes against conventions
  update        File learnings into context-db
  maintain      7-phase audit + reindex

Usage:
  context-db-main-agent.py prompt "user instruction"
  context-db-main-agent.py prompt "user instruction" --mode main-agent
  context-db-main-agent.py review "summary" --model opus --review-type full
  context-db-main-agent.py maintain context-db/subfolder/
  context-db-main-agent.py init

Dependencies: python3 (stdlib only)
"""

# TODO: Implement — Step 4 of unify refactor plan
