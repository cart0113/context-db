This project uses a `context-db/` knowledge base — a hierarchical Markdown
repository of conventions, standards, design decisions, and pitfalls.

## Reading

For non-coding questions, or to search for additional context mid-session, run
`/context-db prompt` with a brief summary of the request. For coding tasks, the
pre-review step below handles context lookup.

Context-db is a starting point — a map, not truth. It documents things you can't
learn from reading any single file. Use it to orient yourself, then verify
against actual project assets (code, configs, docs). If what you find conflicts
with the project, trust the project.

## Pre-Review

Before you start editing files, run:

    /context-db pre-review

This checks your planned changes against project standards and conventions.
Follow what it finds. For trivial changes (typos, one-line fixes), use your
judgment on whether to skip this step.

## Review

After you've completed all changes for the task, run:

    /context-db review

This reviews your changes against project conventions. Fix real issues, use your
judgment on edge cases.

## Writing

When you encounter something the next agent would get wrong or miss — a
correction from the user, a non-obvious convention, a pitfall — suggest running:

    /context-db update

Context-db is the project's memory system. Do not use auto-memory, MEMORY.md, or
any vendor-specific persistence for project knowledge.

For detailed instructions on any capability: `/context-db load-manual <section>`
