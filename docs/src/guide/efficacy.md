# Efficacy

There's a reasonable argument that context engineering hurts more than it helps.
[Research from ETH Zurich](https://www.infoq.com/news/2026/03/agents-context-file-value-review/)
found that LLM-generated context files reduced task success by ~3% and increased
costs by 20%+. Even human-written files showed only marginal gains. Separately,
[Chroma's context rot research](https://www.trychroma.com/research/context-rot)
demonstrated that every model they tested performed worse as input length grew.

I ran experiments to find out whether `context-db` falls into this trap or
avoids it. The short version: verbose `context-db` does hurt — the ETH Zurich
findings are real. But slim `context-db` focused on gotchas and checklists
consistently helped across three different codebases. The benefit wasn't
dramatic on every test. It showed up most clearly in convention-following and
knowing which files to touch, less in raw problem-solving ability. Opus is smart
enough to figure most things out by reading the code — `context-db` just gets it
there faster and with fewer mistakes.

The [test repo](https://github.com/cart0113/git-context-md-tests) is public. The
harness runs `claude -p` in two copies of the same codebase (one with
`context-db`, one without), captures cost/tokens/turns/time from the JSON
output, and resets the source between runs. I manually compared the code after
each test.

## FastAPI

Well-known Python framework. ~5,000-line core files. Likely in training data,
which makes it a harder test for `context-db` — the model already knows the
codebase.

The `context-db` is 182 lines: a file map with section offsets for the huge
`routing.py` and `applications.py` files, gotchas (body embedding, cache keys,
schema caching, scope restrictions), change patterns (the 6-level parameter
threading chain), and design decisions (vendored code, two exit stacks,
middleware ordering).

### Add an `after_endpoint` hook

Thread a new callback through `APIRoute.__init__()`, `get_route_handler()`, and
`get_request_handler()` in `routing.py` — a 5,000-line file.

|       | With context-db | Without | Delta |
| ----- | --------------- | ------- | ----- |
| Cost  | $0.39           | $0.49   | -20%  |
| Time  | 74.2s           | 171.6s  | -57%  |
| Turns | 20              | 16      | +4    |

Both agents found the right locations. But the "with" agent handled both sync
and async callbacks, matching the existing `before_endpoint` pattern:

```python
# With context-db — matches existing pattern
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

The change_patterns.md told the "with" agent to follow the existing
`before_endpoint` pattern. The "without" agent introduced a bug.

### Add `deprecated_message` to OpenAPI

Thread a new parameter through `APIRoute.__init__()` and into OpenAPI generation
in `fastapi/openapi/utils.py`.

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

### Add `on_dependency_resolved` callback

Add a callback to `solve_dependencies()` that fires after each dependency
resolves, passing the callable, resolved value, and whether it came from cache.

|       | With context-db | Without | Delta |
| ----- | --------------- | ------- | ----- |
| Cost  | $0.56           | $0.45   | +25%  |
| Time  | 119.5s          | 120.6s  | ~same |
| Turns | 25              | 22      | +3    |

The same sync/async bug appeared again. The "with" agent used the `isawaitable`
check; the "without" agent used bare `await`. This pattern repeated across all
three FastAPI tests — the `context-db` agent consistently matched existing
codebase conventions while the "without" agent consistently introduced the same
class of bug.

## Gemini CLI

[google-gemini/gemini-cli](https://github.com/google-gemini/gemini-cli) — 457K
lines of TypeScript, released June 2025. A monorepo with 7 packages. Not
something I'd have memorized from training data, and big enough that navigating
blind is expensive.

The `context-db` is 376 lines across a hierarchical structure: architecture
(tool execution flow, model routing, approval mode hierarchy), three
topic-specific subfolders (policy-and-hooks, scheduler, config-and-extensions)
each with gotchas and checklists, and design decisions.

### Add a `ToolTiming` hook event

Add a new hook event type that fires after every tool execution with tool name,
duration, and whether cached. Follow existing patterns.

|       | With context-db | Without | Delta |
| ----- | --------------- | ------- | ----- |
| Cost  | $0.84           | $1.05   | -20%  |
| Time  | 127.4s          | 191.6s  | -34%  |
| Turns | 34              | 32      | +2    |

Both wrote working code. The "with" agent modified 4 files (the correct minimum
from the checklist) and correctly skipped `hookPlanner.ts` (generic, handles all
events) and `hookAggregator.ts` (default case covers it). The "without" agent
modified 5 files, adding a redundant case to `hookAggregator.ts` that falls
through to the same default handler.

Not a bug, but unnecessary code. The checklist guided the "with" agent to the
minimal correct set.

## What verbose context-db looks like (and why it fails)

My first attempt at od-do `context-db` was 671 lines across 13 files — code
summaries, property lists, module layouts, API signatures. The agent with
verbose `context-db` spent 30 turns reading documentation, then wrote code that
was missing properties the "without" agent found by reading the actual source.
Cost $0.69 vs $0.42 without — 64% more expensive for worse code.

The ETH Zurich finding applied directly: the agent followed instructions
diligently, reading every context-db file before touching code, wasting turns on
summaries of things it could have learned faster from the source.

The same happened with a flat (non-hierarchical) gemini-cli `context-db` — $1.35
and 507s with context-db vs $0.84 and 143s without. Restructuring into a
hierarchy with topic subfolders fixed this completely.

## od-do

[od-do](https://github.com/cart0113/od-do) — a Python diagramming toolkit I
wrote. Not in training data. ~180 source files.

The `context-db` is 143 lines: architecture (init sequence trap, coordinate
system, stroke/fill separation), a checklist for adding shapes (5 files in
order), gotchas (exit() in module-level code, PascalCase constructors, nested
diagram debugging), and drawio adaptation notes.

### Add a `DashedBorder` shape

Add a new shape that wraps any existing shape with a dashed border, register it
in the SVG backend, export it.

|       | With context-db | Without | Delta |
| ----- | --------------- | ------- | ----- |
| Cost  | $0.49           | $0.56   | -13%  |
| Time  | 94.7s           | 201.9s  | -53%  |
| Turns | 26              | 15      | +11   |

The "with" agent inherited from `Shape` (getting `bbox`, `points`, `fill_color`,
`stroke_color`, `fill_opacity`, `stroke_opacity` for free), exported correctly
with `from .dashed_border import DashedBorder`, and placed the isinstance
dispatch after existing shapes.

The "without" agent wrote a standalone class, reimplemented all properties
manually, used the wrong export pattern (`from . import dashed_border`), and
missed `fill_color`, `fill_opacity`, `stroke_color`, `stroke_opacity`. The
checklist told the "with" agent exactly which properties were required and which
files to touch.

## What works

1. **Checklists for multi-file changes.** The code shows how each file works.
   `context-db` shows which files must change _together_. This is the single
   highest-value content type.
2. **Gotchas the code doesn't reveal.** Init ordering traps, naming conventions
   not enforced by the language, past bugs that would recur.
3. **Why, not what.** The code shows what. Only `context-db` explains why. And
   "why" prevents the agent from undoing intentional decisions.
4. **Nothing else.** No code summaries. No property lists. No module layouts.
   Verbose context-db is worse than no context-db.

The litmus test: if you removed a document, would the agent make a mistake it
wouldn't otherwise make? If not, the document isn't earning its tokens.
