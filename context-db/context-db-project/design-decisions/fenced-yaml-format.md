---
description:
  Why frontmatter is the standard format and fenced YAML blocks are a supported
  fallback
---

# File Format Design

context-db uses standard YAML front matter (`---` delimiters) as the primary
format for descriptions:

```markdown
---
description: One-line summary
---
```

The build script also supports fenced YAML blocks as a fallback:

````markdown
```yaml description
description: One-line summary
```
````

## Rationale

**Why YAML front matter?** It's the most widely recognized Markdown metadata
format. Every Markdown-aware tool (GitHub, docsify, Jekyll, VS Code) already
understands it. LLMs recognize it without explanation.

**Why support fenced blocks at all?** The fenced format was the original design,
chosen because it can hold multiple named sections (`description`, `config`) in
one file. Front matter only supports one block at the top. When per-folder
config (`ignore`, `follow_symlinks`) was deferred, the multi-block advantage
disappeared and front matter became the simpler choice. Fenced block support was
kept for backward compatibility.

**Why not a separate YAML file?** An earlier version used `CONTEXT.yml`. Merging
metadata into the `.md` file means each context node is just one file:
`<folder>.md` (human-authored). TOCs are generated on demand by the TOC script,
not stored as files.
