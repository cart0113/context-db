# Motivation

## The problem

Teams dump background knowledge into skill files because the format is standard and portable. But skills are designed for *procedures* — filling them with reference material conflates "what to do" with "what to know."

Loading everything eagerly is expensive. A question about the database schema doesn't need coding conventions in context.

## What context-md does

context-md takes the ideas worth keeping from skills — front matter, portability, standardized structure — and applies them to organizing background knowledge.

The key insight is **progressive disclosure**. An LLM reads a lightweight `_toc.md` index that describes what context is available. Based on the current task, it fetches only what it needs. The index is auto-generated from YAML front matter. Humans write context, add a description, and run one script.

## Portability

Any subfolder can be a symlink to a shared resource:

```bash
ln -s /path/to/shared/coding_standards CONTEXT/coding_standards
```

The build script reads descriptions from symlinked folders but never writes into them.

## Relationship to SKILL.md

context-md is a complement to SKILL.md, not a replacement:

- **Skills** — *procedures, what an agent can do*
- **Context** — *what an agent knows, system understanding needed to reason about code updates/changes, answer questions, etc.*
