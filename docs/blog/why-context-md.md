# Why context-md?

*How LLM context management has evolved, and why a dedicated standard helps.*

---

## The Skills Pattern

Anthropic's [SKILL.md standard](https://github.com/anthropics/skills) is a good idea. Write a Markdown file with YAML front matter, put it in `skills/`, and an LLM discovers and follows the procedure. The portability story is even better — a skill folder can be a symlink to a shared repository.

These are ideas worth copying.

## How Teams Actually Use Skills

A pattern that appears again and again:

```
skills/
├── code_review.md          ← a procedure
├── git_workflow.md         ← a procedure
├── project_background.md   ← not a procedure
├── architecture_notes.md   ← not a procedure
└── coding_conventions.md   ← not a procedure
```

The last three are reference material, not procedures. But teams reach for skills anyway because the format is standard, portable, and already supported by their tools.

## The Problem

**Procedures and knowledge are different things.** A skill says: *when X, do Y*. A context document says: *this is what X is*. Mixing them creates confusion.

**Loading everything is expensive.** Skills are often loaded eagerly. Reference material that should only be consulted when relevant consumes tokens on every interaction.

**Discovery semantics differ.** Skills are invoked. Context is consulted. The format gives no signal either way.

## What context-md Does

context-md takes the ideas worth keeping — front matter, portability, standardized structure — and applies them to organizing background knowledge.

The key insight is **progressive disclosure**. An LLM reads a lightweight `_toc.md` index that describes what context is available. Based on the current task, it fetches only what it needs. A question about the database schema doesn't need the UI conventions loaded.

The index is auto-generated from the YAML front matter of context documents and folder description files. Humans write context, add front matter, and run one script. The discovery structure maintains itself.

## Portability

Any subfolder can be a symlink to a shared resource:

```bash
ln -s /path/to/shared/coding_standards CONTEXT/coding_standards
```

The build script reads the description from the symlinked folder but never writes into it. Symlinked directories appear as *(read-only)* in the parent's TOC.

## Relationship to SKILL.md

context-md is not a replacement for SKILL.md. It is a complement:

- **SKILL.md** — *what to do*: procedures, workflows, step-by-step instructions
- **context-md** — *what to know*: background, architecture, conventions, domain knowledge

Keep your skills lean and procedural. Keep your context organized and discoverable.

---

*context-md is open source. Contributions and feedback welcome at
[github.com/cart0113/context-md](https://github.com/cart0113/context-md).*
