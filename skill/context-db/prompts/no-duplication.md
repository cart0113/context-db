# No Duplication

context-db does not duplicate information found in the project's assets
(code, code comments, configs, docs). A copy goes out of date as the project
changes, and the next agent trusts it.

- It holds what cannot be learned by reading the project: reasons for
  decisions, conventions the code does not show, pitfalls, rules imposed from
  outside, domain knowledge, and plans.
- Never write down what can be read from the project: file layouts, function
  signatures, CLI flags, what a function does, walks through code, or anything
  a code comment, the README, or the docs already say. Link to it instead.
- A fact about one piece of code goes in a comment next to that code. Suggest
  the comment to the user and write no note. When the fact is the reason for
  a decision, write the note too, so that the reason is not lost, and delete
  it once the comment is there.
- Where a note and the project's assets disagree, trust the assets, especially
  code, and fix or delete the note. A note that says the code does not follow
  it yet is a requirement still to be built, so it stays.
