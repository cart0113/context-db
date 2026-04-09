# Efficacy

There's a reasonable argument that context engineering hurts more than it helps.
[Research from ETH Zurich](https://www.infoq.com/news/2026/03/agents-context-file-value-review/)
found that LLM-generated context files reduced task success by ~3% and increased
costs by 20%+. Even human-written files showed only marginal gains. Separately,
[Chroma's context rot research](https://www.trychroma.com/research/context-rot)
demonstrated that every model they tested performed worse as input length grew.

The concern is real: verbose context wastes tokens, buries important
information, and can make agents _less_ effective than giving them nothing. I
ran experiments to find out whether `context-db` falls into this trap or avoids
it.

## The experiment

I set up A/B tests using
[this repo](https://github.com/cart0113/git-context-md-tests). Two copies of the
same codebase — one with `context-db` wired up (skills, hooks, rules), one
without. Same prompt, same model (Claude Opus 4.6), same
`--dangerously-skip-permissions`. A Python harness runs `claude -p` in each
folder and captures cost, tokens, turns, and time from the JSON output. After
each run I manually compared the code both agents wrote.

Two test projects:

- **[od-do](https://github.com/cart0113/od-do)** — a Python diagramming toolkit
  I wrote. Not in training data. ~180 source files.
- **FastAPI** — well-known Python framework. ~5,000-line core files. Likely in
  training data, which makes it a harder test for `context-db`.

## What I learned about verbose context-db

My first attempt at `context-db` was verbose — 671 lines across 13 files for
od-do. Code summaries, property lists, module layouts, API signatures. The kind
of thorough documentation that _feels_ helpful.

It wasn't. The agent with verbose `context-db` spent 30 turns reading
documentation, then wrote code that was missing properties the "without" agent
found by reading the actual source files. The verbose `context-db` cost $0.69 vs
$0.42 without — 64% more expensive for worse code.

The ETH Zurich finding applied directly: the agent followed instructions
diligently, leading to excessive exploration. It read every context-db file
before touching the code, wasting turns on summaries of things it could have
learned faster by reading the source.

## Slim context-db: gotchas and checklists only

I stripped the od-do `context-db` from 671 lines to 143. Removed all code
summaries, property lists, and module layouts. Kept only:

- **Gotchas.** The init sequence trap (set params before `super().__init__()` —
  because super calls `draw()`). The `exit()` in module-level code bug.
- **Checklists.** "Adding a new shape? Touch these 5 files in this order."
- **Why, not what.** Why SVG stroke and fill are rendered as separate elements.

### od-do: add a `DashedBorder` shape

|       | With context-db | Without | Delta |
| ----- | --------------- | ------- | ----- |
| Cost  | $0.49           | $0.56   | -13%  |
| Time  | 94.7s           | 201.9s  | -53%  |
| Turns | 26              | 15      | +11   |

The "with" agent inherited from `Shape` (getting `bbox`, `points`, `fill_color`,
`stroke_color`, `fill_opacity`, `stroke_opacity` for free), exported correctly
with `from .dashed_border import DashedBorder`, and placed the isinstance
dispatch after existing shapes.

The "without" agent wrote a standalone class, reimplemented all the properties
manually, used the wrong export pattern (`from . import dashed_border`), and
missed `fill_color`, `fill_opacity`, `stroke_color`, `stroke_opacity` entirely.
The checklist in `context-db` told the "with" agent exactly which properties
were required and which files to touch. The "without" agent had to figure it out
from the code and got an incomplete picture.

### FastAPI: add an `after_endpoint` hook

|       | With context-db | Without | Delta |
| ----- | --------------- | ------- | ----- |
| Cost  | $0.39           | $0.49   | -20%  |
| Time  | 74.2s           | 171.6s  | -57%  |
| Turns | 20              | 16      | +4    |

The task: thread a new callback through `APIRoute.__init__()`,
`get_route_handler()`, and `get_request_handler()` in `routing.py` — a
5,000-line file.

Both agents found the right locations and placed the hook correctly (after
`run_endpoint_function()`, before response validation). But the "with" agent
handled both sync and async callbacks:

```python
# With context-db — matches existing before_endpoint pattern
if after_endpoint is not None:
    result = after_endpoint(request, raw_response, solved_result.values)
    if inspect.isawaitable(result):
        await result
```

```python
# Without context-db — async only, sync callbacks crash
if after_endpoint is not None:
    await after_endpoint(request, raw_response, solved_result.values)
```

The `context-db` change_patterns.md told the "with" agent to follow the existing
`before_endpoint` pattern. The "without" agent found the right location but
didn't fully match the pattern, introducing a bug.

### FastAPI: add `deprecated_message` to OpenAPI

|       | With context-db | Without | Delta |
| ----- | --------------- | ------- | ----- |
| Cost  | $1.97           | $1.40   | +41%  |
| Time  | 310s            | 214.7s  | +44%  |
| Turns | 60              | 42      | +18   |

The "with" agent cost more — but it threaded `deprecated_message` through the
full registration chain (decorators, `APIRouter`, `FastAPI` class), making the
feature actually usable from `@app.get("/foo", deprecated_message="Use /bar")`.
The "without" agent only wired it through `APIRoute.__init__()` and the OpenAPI
generator — technically correct for the prompt, but the feature wouldn't be
accessible from the API developers actually use.

### FastAPI: add `on_dependency_resolved` callback

|       | With context-db | Without | Delta |
| ----- | --------------- | ------- | ----- |
| Cost  | $0.56           | $0.45   | +25%  |
| Time  | 119.5s          | 120.6s  | ~same |
| Turns | 25              | 22      | +3    |

The task: add a callback to `solve_dependencies()` that fires after each
dependency resolves, passing the callable, resolved value, and whether it came
from cache. Both agents found the right place in the recursive resolution loop,
tracked `from_cache` correctly, and threaded the callback through from
`get_request_handler()`.

The same sync/async bug appeared again. The "with" agent used the `isawaitable`
check; the "without" agent used bare `await`. This pattern repeated across all
three FastAPI tests — the `context-db` agent consistently matched existing
codebase conventions while the "without" agent consistently introduced the same
class of bug.

## What makes context-db effective

The research says verbose context hurts. My experiments confirm it. But slim,
targeted context helps — consistently.

The pattern that works:

1. **Checklists for multi-file changes.** The code shows how each file works.
   `context-db` shows which files must change _together_. This is the single
   highest-value content type.
2. **Gotchas the code doesn't reveal.** Init ordering traps, naming conventions
   that aren't enforced by the language, past bugs that would recur.
3. **Why, not what.** The code shows what. Only `context-db` explains why. And
   "why" prevents the agent from undoing intentional decisions.
4. **Nothing else.** No code summaries. No property lists. No module layouts.
   Reading a 200-line source file is faster and more complete than reading prose
   about it.

The litmus test: if you removed a document, would the agent make a mistake it
wouldn't otherwise make? If not, the document isn't earning its tokens.
