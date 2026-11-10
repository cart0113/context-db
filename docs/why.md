# Why it works this way

Context files are both the cause of, and solution to, many agent problems.
Agents given files that describe code state trust those descriptions, read less
actual code, and perform worse when the descriptions drift. Agents given no
guidance default to their training and miss every project-specific constraint.
context-db is an attempt to stay on the right side of that line.

## When context hurts

[Research from ETH Zurich](https://www.infoq.com/news/2026/03/agents-context-file-value-review/)
found that LLM-generated context files reduced task success by about 3% and
increased cost by more than 20%. Hand-written ones showed only marginal gains.
Separately,
[Chroma's context-rot research](https://www.trychroma.com/research/context-rot)
showed every frontier model performing worse as input length grew, well below
context limits.

The mechanism is the same in both. The agent trusts the file, reads less code,
and amplifies whatever drift exists between description and reality. A note that
says "the auth middleware lives in `auth/middleware.py`" stays in the agent's
head after the file is renamed.

## Where context-db departs from the LLM wiki

The format comes from Andrej Karpathy's
[LLM wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
pattern, which Google formalized as the Open Knowledge Format. In that pattern
the wiki compiles external sources the model cannot cheaply re-read, so every
ingested source adds pages and more is better.

A codebase is different. The raw source is right there and the agent can read
it. A page that restates the code is a second, staler copy. So context-db takes
the format and not the habit of accumulation: most sessions store nothing.

| LLM wiki             | context-db                                    |
| -------------------- | --------------------------------------------- |
| Raw sources          | The codebase, plus background bundles         |
| The wiki             | `context-db/<name>-project/`                  |
| The schema           | The skill's prompts and the `ON_*.md` files   |
| Ingest, query, lint  | `update`, `prompt`, the `index` lint          |
| `index.md`           | Generated `index.md`                          |
| `log.md`             | Git history                                   |

## How that shapes the instructions

The instructions the commands print carry these findings directly. From
`prompt`:

> Context-db is a map, not the territory. Use it to orient, then verify against
> the project's assets (code, configs, docs). Where they conflict, trust the
> project's assets, especially code, and tell the user what is out of date.

If the project disagrees with context-db, the project wins. That is what keeps
an agent from following stale context off a cliff.

Reading is deliberately narrow:

> Open a file only when its description says it bears directly on the
> instruction. ... Skip everything else. Reading widely dilutes what matters.

Writing is narrower still. `update` opens with a gate, before any mechanics:

> Most sessions produce nothing worth storing. That is the normal outcome, not a
> failure. Every addition dilutes what is already there.

The gate comes first on purpose. Models are trained to produce output, so once
the writing instructions have loaded, "nothing to add" feels like failure.

## Why re-inject

Standards loaded at session start are compressed away after fifteen or twenty
turns. By turn forty the agent is back on its training defaults. `prompt` is a
deliberate moment where the relevant slice is fetched again, immediately before
the work it applies to. That is also why nothing loads at startup.

## One negative result, one positive

Same project, two knowledge bases, opposite outcomes. The project was a Python
diagramming toolkit of about 180 source files, not in training data. The task
was to add a new shape class.

**A verbose knowledge base hurt.** The first attempt was 671 lines across 13
files: code summaries, property lists, module layouts, API signatures. The agent
spent 30 turns reading it, then wrote code missing properties that the
no-context agent found by reading the source. It cost $0.69 against $0.42.

**A slim one helped.** Cut to 143 lines: architecture, a five-file checklist for
adding shapes, a handful of gotchas. Same task, same model.

|      | With context-db | Without | Delta |
| ---- | --------------- | ------- | ----- |
| Cost | $0.49           | $0.56   | -13%  |
| Time | 94.7s           | 201.9s  | -53%  |

With the slim knowledge base the agent inherited from the right base class,
exported the shape correctly, and touched the right five files. Without it, the
agent wrote a standalone class, reimplemented properties by hand, and missed
four of them.

The same effect showed up in other tests on FastAPI and gemini-cli: a slim
knowledge base of gotchas and checklists helps, and a verbose one hurts.

## The test for every entry

If this file were removed, would the agent make a mistake it would not otherwise
make? If not, the file is not earning its tokens, and by the ETH Zurich finding
a file that does not earn its tokens has negative value.
