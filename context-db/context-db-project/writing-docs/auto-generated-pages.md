---
description:
  docs/src/reference/cli.md is generated from real dispatcher --help output and
  prompt templates so it cannot drift from the agent-facing surface. The rule
  and the generator coupling that supports it.
---

# Auto-generated docs pages

## The rule

When a doc would duplicate canonical agent-facing text — the literal prompt-
template body the agent reads, or the literal `--help` of the CLI — generate the
doc, do not paraphrase it. Paraphrases drift; the generated doc is the project's
evidence that it has not.

## What is generated today

| Page                        | Generator                    | Source                                                                                     |
| --------------------------- | ---------------------------- | ------------------------------------------------------------------------------------------ |
| `docs/src/reference/cli.md` | `bin/build-cli-reference.py` | dispatcher `--help` plus prompt templates under `templates/skills/.../prompts/main-agent/` |

The page starts with a `> [!note] Auto-generated. Do not edit by hand.` banner.
Edits go to the generator script and / or the source files; the page is
overwritten on next run.

The generator's `SUBCOMMANDS` list pairs each command with its instruction
template. When a command or template is added/removed/renamed, update that list.

## Pre-commit hook

`hooks/pre-commit` regenerates `cli.md` when the dispatcher, prompt templates,
or `bin/build-cli-reference.py` changes. The generator is idempotent.

## When NOT to auto-generate

If a page is genuinely user-intent material (worked examples, "what would I use
this for", per-agent invocation), it stays hand-written. The generator pattern
only applies where the doc is a window onto something the agent already reads at
runtime.
