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

What does NOT belong:

- Code state, step-by-step instructions, anything derivable in 30 seconds with
  ls/grep/read

[end write-content-guide]
