---
description:
  What we learned building the sub-agent — late-session recall problem, why
  pre-loading fails, prompt engineering for haiku, relative paths, selectivity.
  Still valid for the unified /context-db skill.
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

## Cheap models need structured output constraints

Haiku ignores "do NOT help with the task" instructions. It treats the user's raw
prompt as a request to itself. Two fixes were needed:

1. **Structured output format** — "respond with ONLY verbatim snippets"
   constrains the output shape, making task-help harder
2. **Wrapping the prompt** — `Developer's prompt: <text>` reframes it as a
   lookup request, not a task request. Without this wrapper, haiku acts as a
   coding assistant instead of a knowledge lookup service.

## Content-first ordering matters

Putting the prompt before the navigation instructions produces better results.
The model reads what it needs to find context for, then navigates with that
filter in mind. Instructions-first ordering caused the model to navigate
generically and miss relevant files.

## The rule is the durable anchor

The session-start hook fires once. The SKILL.md loads on demand. But the rule
file stays in context for the entire session — it survives compression. The rule
is where "call the subagent" instructions must live to be reliable at turn 50.

## Constrain navigation to TOC + Read only

Without constraints, haiku adds defensive commands (`find`, `ls -la`,
`head -50`, `2>/dev/null`) that waste turns. Telling it "Do not use find, grep,
or ls" produces clean 2-3 step navigation.

## All paths must be relative to cwd

Early versions resolved the TOC script and context-db to absolute paths. The
subagent saw `/Users/.../GIT_CONTEXT_DB/templates/skills/...` for the TOC script
and tried to read files relative to that location — causing double-reads (wrong
path, then self-correction). Similarly, `git rev-parse --show-toplevel` returned
a parent git repo instead of the actual project directory.

Fix: all paths are relative to cwd (the project root where the user runs the
script). TOC script is `.claude/skills/.../context-db-generate-toc.sh`,
context-db is `context-db/`. No absolute paths, no symlink resolution, no git
root detection. The subagent sees the same paths a developer would use.

## Main agent must wait for subagent before exploring codebase

Without explicit wait instructions, the main agent starts exploring the codebase
in parallel with the subagent call — defeating the purpose of subagent-first
lookup. The wait instruction must be in the instructions-mode output (not the
sub-agent prompt) so it governs the main agent's behavior.

## Main agents don't follow standards reliably — feed them before they start

The main agent often ignores standards loaded at session start. By the time it's
writing code, the standards have faded into background context. Pre-review mode
forces the agent to call for applicable standards _immediately before starting
edits_ as a workflow step. This is a structural fix — telling the agent "follow
the standards" in instructions doesn't work reliably.

## Do not anthropomorphize in docs or prompts

Don't call the main agent "the expert" or give it human qualities. Frame
sub-agent responses as "additional context" — not as advice from a junior to a
senior. The goal is to inform, not to establish a hierarchy between models.

## Review type separation matters

`context-db` review only flags issues backed by a convention, each critique
citing its source. `full` adds a general review section. Separating these
prevents the model from mixing convention-backed critiques with general opinions
— the main agent needs to know which critiques have authority behind them.

## Self-reference guard for user-prompt

Without scope filtering, the subagent returns information about context-db
itself when asked about a project that uses context-db. The system prompt must
constrain the subagent to only return information found in the knowledge base,
not about the knowledge base system itself.
