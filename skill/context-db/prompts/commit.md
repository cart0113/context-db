# Commit

After the update, commit every file touched in this session: code, docs,
configuration, `{cdb}/`, everything. The scope is the whole session, not only
the context-db update. If `git status` shows changes outside `{cdb}/`, they
belong in this commit too, unless the user has said otherwise.

Before writing the message, check the folders listed above for commit-message
standards and follow them if any exist. Otherwise say what was learned and why
it matters: corrections, pitfalls, decisions, new conventions. The bar is lower
than for context-db entries, so capture session learning freely. When there is
nothing notable, a simple message is fine.

{push}
