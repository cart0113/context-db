---
description:
  Prompt template sections use H1 markdown headers in Title Case — one H1 per
  file, no closing tags. Replaces old bracket-tag convention.
---

Prompt templates use a single H1 markdown header as the section delimiter:

```
# Sub Agent Role

Content here...
```

Not bracket tags (old convention, removed):

```
[sub-agent-role]
Content here...
[end sub-agent-role]
```

One H1 per template file. The H1 is the section identity — no closing tag
needed. Sub-sections within a template use H2/H3 as normal markdown.

Headers use Title Case: `# Read Mechanics`, `# Spawn Context Db Pre Review`,
`# Main Prompt`. The `print_section()` function in the main-agent script
converts kebab-case tag names to Title Case automatically.

Headers must be descriptive and self-documenting. `# Sub Agent Output Format`
tells you what the block does at a glance. `# Output` or `# Instructions` would
be too generic — when multiple sections compete for the model's attention,
descriptive names let it skip irrelevant blocks.

Dynamically injected sections (user prompts, instructions) also use H1 headers:

- `# Main Prompt` — the user's prompt for the `prompt` command
- `# User Guidance` — optional guidance for review/pre-review commands
- `# Update User Instructions` — instructions for update commands
