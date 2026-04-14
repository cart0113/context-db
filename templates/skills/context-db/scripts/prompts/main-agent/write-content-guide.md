[write-content-guide]

Update context-db only if you encountered something that would mislead the next
agent — a non-obvious dependency, a constraint invisible in the project assets,
a convention the agent wouldn't know, or a correction from the user.

Update existing files when they cover the topic. Create new files only for
genuinely new topics. Delete content that has drifted into code summary. A
smaller, accurate context-db outperforms a larger, comprehensive one.

Be brief and direct. State the fact, the convention, the pitfall — no
exposition, no justification unless the "why" is the whole point. If a file
reads like documentation, it's too long.

What belongs — things the next agent would get wrong or miss:

- Conventions, corrections from the user, pitfalls, design rationale, domain
  knowledge

Prefer cross-references over duplication — two sources of truth will drift:

- Code and config: never restate. The agent can read them.
- Docs: point to them when they cover a topic well, but make the context-db
  entry self-contained enough to be useful if the link breaks. State the insight
  briefly, link the source, add what the source doesn't say.

What does NOT belong:

- Code state, step-by-step instructions, anything derivable from project assets

[end write-content-guide]
