---
title: Project Overview
description: What context-md is, why it was built, and how it differs from SKILL.md
---

# context-md — Overview

## What It Is

A lightweight standard for organizing background knowledge and project context in
Markdown files so LLMs can discover and consume it efficiently.

The core artifact is `<folder>_toc.md` — a generated table-of-contents that indexes
every context resource in a directory. An LLM reads the TOC first, then fetches only
what it needs.

## Why It Was Built

Many teams use SKILL.md for general reference material — architecture notes, coding
conventions, onboarding guides. Skills are designed for *procedures*, not knowledge.
This misuse degrades skill subsystem performance and conflates "what to do" with
"what to know."

context-md preserves the best ideas from SKILL.md (standardized structure, portability
via symlinks, front matter metadata) and applies them specifically to context.

## What It Is Not

Not a replacement for SKILL.md. A complement.

- **SKILL.md** — what to do: procedures, workflows, step-by-step instructions
- **context-md** — what to know: background, architecture, conventions, domain knowledge
