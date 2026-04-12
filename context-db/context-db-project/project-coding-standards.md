---
description:
  context-db-specific coding standards — overrides and additions to
  general-coding-standards. No shims, no defensive .get(), triple-quote editable
  text blocks.
---

# context-db Project Coding Standards

These supplement (and can override) the general coding standards in
`general-coding-standards/`.

## No backward compatibility shims

When renaming or restructuring, update directly. Do not add shims, aliases, or
fallback handling that supports old names alongside new ones. If callers need
updating, update them. Shims accumulate and create two systems to maintain.

This applied when renaming modes (ask → user-prompt, review → code-review, scope
→ review-type): every reference was updated, no old-name fallbacks added.

## No defensive `.get()` calls

Do not use `dict.get(key, default)` as a defensive measure against missing keys.
If a key is required, access it directly — let the KeyError surface. If a key is
genuinely optional, document why in a comment. Defensive `.get()` hides bugs and
makes required fields appear optional.

## Triple-quote all editable text blocks

Any string in Python that a developer is expected to hand-edit (role prompts,
instructions output, workflow text) must use triple-quoted strings, even if the
content is a single line. Triple-quotes signal "this is user-facing content" and
make multi-line editing natural without escape sequences.

```python
# Wrong — hard to edit, no visual signal
role = "You are a subagent. Return only bullet points."

# Right — easy to edit, clearly user-facing content
role = """
You are a subagent. Return only bullet points.
"""
```
