---
description:
  What we learned building the subagent — constrained navigation, running from
  context-db/, the late-session recall problem, why pre-loading fails, prompt
  engineering for haiku compliance
---

# Lessons Learned

## The late-session recall problem

Manual mode loads context at session start. After 15-20 turns, it gets
compressed away. By the time a user says "commit everything" on turn 40, the
agent has lost all git standards. The subagent reads fresh every call — turn 1
or turn 50, same quality. This is the strongest practical argument for subagent
mode.

## Pre-loading all files breaks the B-tree

The first implementation had Python read every `.md` file and stuff them into
the system prompt. Problems:

- Python can't judge which files are relevant — that's a language task
- Doesn't scale with large knowledge bases
- Cross-project symlinks broke (Python's `rglob` doesn't follow directory
  symlinks in Python 3.9)
- Bypasses the description-based routing that context-db is designed for

Fix: let the model navigate with Bash and Read tools, same as manual mode.

## Cheap models need structured output constraints

Haiku ignores "do NOT help with the task" instructions. It treats the user's raw
prompt as a request to itself. Two fixes were needed:

1. **Structured output format in the role prompt** — "respond with ONLY bullet
   points" constrains the output shape, making task-help harder
2. **Wrapping the prompt** — `Developer's prompt: commit everything to git`
   reframes it as a lookup request, not a task request. Without this wrapper,
   haiku acts as a coding assistant instead of a knowledge lookup service.

## Content-first ordering matters

Putting the prompt before the navigation instructions produces better results.
The model reads what it needs to find context for, then navigates with that
filter in mind. Instructions-first ordering caused the model to navigate
generically and miss relevant files.

## The rule is the durable anchor

The session-start hook fires once. The SKILL.md loads on demand. But the rule
file stays in context for the entire session — it survives compression. The rule
is where "call the subagent" instructions must live to be reliable at turn 50.

## One model per mode

Early versions used haiku for file selection and sonnet for synthesis within a
single mode. This was confusing to configure and debug. One model per mode is
cleaner — the configured model handles the entire call.

## Ask mode needs explicit scope constraints

Without scope filtering, the subagent returns information about context-db
itself (architecture, installation, etc.) when asked about a project that
happens to use context-db. Two filtering rules were needed in the ask mode role
prompt:

1. **Source constraint** — "Only return information found in the context-db/
   folder" keeps the model from drawing on its training knowledge or other
   in-context files.
2. **Self-reference guard** — "Do not return information about context-db
   itself" prevents the subagent from surfacing context-db meta-knowledge as if
   it were project knowledge.

These rules are effective when the context-db/ folder does not contain
self-referential files. Confirmed working against an external fastapi test repo.

## Main agent must wait for subagent before exploring codebase

Without explicit wait instructions, the main agent starts exploring the codebase
in parallel with the subagent call — defeating the purpose of subagent-first
lookup. The instructions mode output now includes:

> "Wait for the response before taking other actions — do not explore the
> codebase or start work in parallel."

This must be in the instructions-mode output (which goes into the rule file),
not just the role prompt, so it governs the main agent's behavior.

## Run from inside context-db/, not the project root

Running `claude -p` with `cwd=context-db/` and `--bare` sandboxes the subagent
to just the markdown files. No rules, no skills, no CLAUDE.md — it can't wander
into the codebase. The `--context-db` flag defaults to `.` (current directory)
so the expected flow is `cd context-db/ && run the script`.

## Constrain navigation to TOC + Read only

Without constraints, haiku adds defensive commands (`find`, `ls -la`,
`head -50`, `2>/dev/null`) that waste turns. Telling it "Do not use find, grep,
or ls. Only the TOC script and Read." produces clean 2-3 step navigation.

## Absolute TOC path is a breadcrumb

The TOC script path is absolute (e.g.,
`/path/to/skills/context-db-manual/ scripts/...`). Haiku sees it and tries to
read files relative to that location. Adding "All files are relative to your cwd
(.). The TOC script is an external tool — never read files from its directory."
fixes this, but haiku still occasionally tries the wrong path on first attempt
and self-corrects.

## stream-json for live output

`--output-format stream-json --verbose` lets the script print tool calls as they
happen. Without this, `claude -p` buffers everything and the caller sees nothing
until the full response is ready — which takes 20-30 seconds.
