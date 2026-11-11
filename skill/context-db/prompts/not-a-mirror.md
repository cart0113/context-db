# Context-db Is Not a Mirror of the Code

Context-db holds what an agent cannot learn by reading the project: why
decisions were made, conventions the code does not show, pitfalls, rules
imposed from outside, domain knowledge, and plans. Everything else already has
a home in the project's assets (code, code comments, configs, docs), and lives
there only.

A note that restates the project is a second copy. The copy drifts as the code
changes, nobody notices, and the next agent trusts it over the code. So:

- Never write down what can be read from the project: file layouts, function
  signatures, CLI flags, what a function does, step-by-step walks through code,
  or anything a code comment already says. Link to the code instead.
- A fact about one piece of code belongs in a comment next to that code, not in
  a note. Suggest the comment to the user instead of writing the note.
- Where a note and the project disagree, trust the project's assets,
  especially code, and fix or delete the note. The exception is a note that
  says the code does not follow it yet: that is a requirement still to be
  built, not a stale note.

The test for every line: could an agent learn this by reading the code and its
comments? If so, it does not belong in context-db.
