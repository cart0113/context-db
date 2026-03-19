---
description: Why context-md uses fenced YAML blocks instead of front matter or a separate YAML file
---

# Fenced YAML Format

The `<folder>.md` file uses fenced code blocks for structured data:

~~~
```yaml description
description: One-line summary
```

```yaml config
ignore: [scratch, old_docs]
```
~~~

## Rationale

**Why not YAML front matter?** Front matter (`---` delimiters) is standard for
individual documents, and context-md uses it there. But for the folder description
file, we need two distinct sections (description and config) in a file that also
contains freeform Markdown prose. Front matter only supports one block at the top
of the file.

**Why not a separate YAML file?** An earlier version used `CONTEXT.yml`. This works
but adds an extra file per directory. Merging config into the `.md` file means each
context node has exactly two files: `<folder>.md` (human) and `<folder>_toc.md`
(generated). Fewer files, simpler.

**Why fenced blocks specifically?** Fenced code blocks (```` ```yaml description ````)
are trivially parseable with awk — look for the opening fence, read key-value pairs,
stop at the closing fence. They render cleanly in any Markdown viewer (as a YAML code
block). And the block label (`description`, `config`) makes the purpose explicit.
