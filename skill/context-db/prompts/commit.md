# Commit

After the update, commit every file touched in this session: code, docs,
configuration, `{cdb}/`, everything. The scope is the whole session, not only
the context-db update. If `git status` shows changes outside `{cdb}/`, they
belong in this commit too, unless the user has said otherwise.

If one of the folders listed above holds a commit-message standard, write the
message in that format. In either case, use the message to say what was learned
and why it matters: corrections, pitfalls, decisions, new conventions. The bar
is lower than for context-db entries, so capture session learning freely. When
there is nothing notable, a simple message is fine.

{push}
