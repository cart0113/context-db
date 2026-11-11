<!--
Everything in this file outside HTML comments is added to every
`/context-db prompt`, near the end, just before the user's instruction. Edit it by
hand whenever you like.

These are the project's rules, shared with everyone. Rules that are only yours
go in ON_PROMPT.local.md next to this file. It is added after this one, and
every *.local.md file in this folder is gitignored.

Keep it to the few rules the agent must see every time: every line is read on
every run. An empty file adds nothing.
-->

You may update the knowledge base as you work, without being asked, when you
learn something the next agent would get wrong without it: a correction from
the user, a decision and its reason, a pitfall. Run
`{update_cmd} '<what you learned>'` and follow what it prints. Keep the bar
high, tell the user in one line each time, and never commit on your own.
