---
title: Project Overview
description: What context-md is, why it was built, and how it differs from SKILL.md
---

# context-md — Project Overview

## What It Is

context-md is a lightweight standard for organizing background knowledge and project context in Markdown files so that LLMs can discover and consume it efficiently.

The core artifact is `CONTEXT/CONTEXT_TOC.md` — a structured table-of-contents file that indexes everything an LLM might want to know about a project or module. Each entry in the TOC is a one-line description pulled automatically from the front matter of the source file.

## Why It Was Built

Two observations motivated this project:

**Observation 1 — SKILL.md misuse.** Many development teams reaching for a portable, standardized way to share project context with LLMs have landed on the SKILL.md format. Skills are designed for *procedures*: step-by-step instructions that an LLM should follow. But teams use them for general reference material — architecture diagrams, coding conventions, onboarding guides. This is understandable (the format is clean and well-supported) but creates problems:

- Skill subsystems have bounded capacity; filling them with reference material leaves less room for actual procedures
- Mixing knowledge and procedures in the same namespace makes skills harder to reason about
- Skill invocation implies "follow these instructions" — the wrong semantic for passive context

**Observation 2 — Portability matters.** One of SKILL.md's most powerful features is that a skill folder can be a symlink to a shared repository. A team maintaining a coding style guide can publish it once and every project just symlinks it. context-md preserves this portability: any `CONTEXT/` subtree can be a symlink.

## What It Is Not

context-md is not a replacement for SKILL.md. It is a complement. Skills remain the right tool for procedural instructions. context-md is specifically for the knowledge that informs those procedures — the *why* and *what* rather than the *how*.

## Design Goals

1. **Progressive discovery** — never load all context; load only what's relevant
2. **Modular** — each `CONTEXT/` directory is self-contained and portable
3. **Auto-maintained** — TOC tables are generated from front matter; humans only write docs
4. **Minimal tooling** — a single bash script and an optional Python formatter; no build system
5. **Transparent** — the format is plain Markdown; every file is human-readable
