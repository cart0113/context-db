# Why it works this way

Giving an agent notes about your project can help it or hurt it. This page
covers what the research says, and how context-db's rules follow from it.

## Notes can make an agent worse

[Researchers at ETH Zurich](https://www.infoq.com/news/2026/03/agents-context-file-value-review/)
tested coding agents with and without context files such as `AGENTS.md`. Files
written by an LLM lowered the success rate by about 3% and raised cost by more
than 20%. Files written by people helped only a little.

[Chroma's study of context length](https://www.trychroma.com/research/context-rot)
found that every model it tested did worse as its input grew, long before the
context window was full.

The two results fit together. An agent that is handed a file about the project
trusts it, reads less of the code, and repeats whatever the file gets wrong. A
note saying "the auth middleware lives in `auth/middleware.py`" stays in the
agent's head after someone renames the file.

## What context-db does about it

**It keeps notes out of the way until they are needed.** Nothing is loaded when
a session starts. The agent reads the knowledge base only when you run a
command, and then it reads an index and opens only the files that match the
task.

**It loads notes at the moment of work.** Rules that are loaded at the start of
a session fade. On a long session they are compacted away, and by turn forty the
agent is back on its defaults. `prompt` fetches the relevant rules again,
immediately before the work they apply to.

**It tells the agent that the code wins.** Every `prompt` includes this:

> Context-db is a map, not the territory. Use it to orient, then verify against
> the project's assets (code, configs, docs). Where they conflict, trust the
> project's assets, especially code, and tell the user what is out of date.

**It asks whether to write before it says how.** `update` opens with a question:
would the next agent get something wrong without this? Then it says:

> Most sessions produce nothing worth storing. That is the normal outcome, not a
> failure. Every addition dilutes what is already there.

The question comes first on purpose. Models are trained to produce something.
Once the instructions for writing have loaded, writing nothing feels like
failing.

## How this differs from an LLM wiki

context-db's file format comes from Andrej Karpathy's
[LLM wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
idea, by way of the [Open Knowledge Format](okf.md). In an LLM wiki, the wiki
grows with every source the LLM reads, because the LLM cannot cheaply read
those sources again.

In a code repository the source is the code, and the agent can read it at any
time. A page that repeats the code is a second copy that goes out of date. So
context-db keeps only what the code cannot say.

## A test on a real project

The project was a Python diagramming toolkit of about 180 source files that was
not in any model's training data. The task was to add a new shape class. Each
comparison below was run separately, so the cost with no notes differs between
them.

With a long knowledge base, the agent did worse than with none. The knowledge
base was 671 lines in 13 files: code summaries, property lists, module layouts,
API signatures. The agent spent 30 turns reading it, then wrote code that was
missing properties. The agent with no notes found those properties by reading
the source. The run cost $0.69, against $0.42 with no notes.

With a short knowledge base, the agent did better. It was cut to 143 lines: the
architecture, a checklist of the five files to change when adding a shape, and
a few gotchas.

| | With the short knowledge base | With none |
| --- | --- | --- |
| Cost | $0.49 | $0.56 |
| Time | 95 seconds | 202 seconds |

With the short knowledge base the agent inherited from the right base class,
exported the shape correctly, and changed the right five files. With none, it
wrote a standalone class, rebuilt properties by hand, and missed four of them.

Other tests, on FastAPI and gemini-cli, went the same way.

## The test for every note

Ask this of each file. If it were deleted, would the agent make a mistake that
it does not make now? If the answer is no, delete it.
