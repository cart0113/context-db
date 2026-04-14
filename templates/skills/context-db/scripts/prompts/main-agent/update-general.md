[update-instructions]

Think about your current session — corrections the user made, conventions you
learned, pitfalls you hit, decisions and why. Then decide: would the next agent
get something wrong or miss something without this knowledge? If not, tell the
user there's nothing to add. That is a good outcome — not every session produces
context-db updates.

If there is something worth persisting, use the read mechanics above to see
what's already documented. Update existing files when they cover the topic.
Create new files only for genuinely new topics. You can use other tools — like
running git diff — to provide additional context on what to store.

Do not persist things derivable from the code — CLI flags, function signatures,
file layouts. The code is the source of truth for those.

If you are unsure or want clarification, ask the user.

Do not run /context-db update yourself. The user invokes this. If you need to
write to context-db later, use the read mechanics and write-file-format above
directly.

[end update-instructions]
