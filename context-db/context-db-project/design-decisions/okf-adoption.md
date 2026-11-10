---
type: Decision
description:
  Why v0.1 adopted the Open Knowledge Format (OKF) as the file format while
  keeping context-db's own operating rules — the lineage from Karpathy's LLM
  wiki, what OKF requires, which parts are used and skipped, the risks of
  tracking a young spec, and the primary sources.
---

# OKF adoption

The user-facing explainer is [docs/okf.md](../../../docs/okf.md). This file
records the reasoning and what to re-check when OKF changes.

## Lineage (all dates from primary sources)

1. **2026-04-04** — Karpathy's LLM Wiki gist. An idea file, not a standard: an
   LLM maintains a wiki of interlinked Markdown instead of re-deriving answers
   from raw documents on every query.
2. **2026-06-12** — Google Cloud announces OKF v0.1, saying it "formalizes the
   LLM-wiki pattern". Karpathy did not write OKF; Google did, citing him.
3. **2026-07-24** — OKF v0.2 adds provenance, trust, lifecycle, and attested
   computations. It also renamed two v0.1 fields.
4. **2026-08-11** — the spec moves from `knowledge-catalog/okf` to
   `GoogleCloudPlatform/open-knowledge-format`.
5. **2026-11-06** — PR #63 there, by a Google collaborator, deprecates that
   repository in favor of a vendor-neutral `open-knowledge-format` org where
   v0.3 is in progress. The org had no public repositories as of 2026-11-10, so
   v0.2 is the latest spec anyone can read.

## Why adopt it

context-db and the LLM wiki were built independently and converged on the same
shape. Conformance costs one frontmatter key (`type`). In return the format has
a name and a specification that context-db no longer has to write, and the
files are readable by Obsidian, GitHub, and OKF tools.

OKF gives nothing on the operating side: when to read, what is worth storing,
the wip loop. Those stay context-db's own.

## Where context-db deliberately differs

- **Accumulate versus cut.** An LLM wiki compiles sources the model cannot
  cheaply re-read, so more pages is better. A coding agent can read the code,
  and generated context files measurably hurt. context-db keeps its rule that
  most sessions store nothing.
- **Trust and provenance keys are not written.** See
  [frontmatter-fields.md](./frontmatter-fields.md).
- **Links are file-relative**, not the bundle-relative form OKF recommends. See
  [links-and-symlinks.md](./links-and-symlinks.md).
- **The index is flat**, not grouped by type as the reference tool does. See
  [static-index.md](./static-index.md).
- **Folders get a descriptor file.** OKF has no field for a folder's
  description; its reference implementation has an LLM synthesize one from the
  folder's children. A descriptor is deterministic and reviewable.

## What the reference implementation checks

Its parser (`src/reference_agent/bundle/document.py`) loads the frontmatter with
PyYAML and requires a non-empty `type`. Nothing else is validated. The test
`test_frontmatter_is_real_yaml_and_the_parser_agrees_with_a_yaml_library` makes
the same check on every shipped file, so the hand-rolled parser cannot drift
from real YAML unnoticed.

## Risks and what contains them

- **The spec is moving.** Two renames between v0.1 and v0.2, three homes in five
  months, v0.3 not yet visible. context-db uses only frontmatter with `type` and
  `description`, `index.md`, links (all unchanged since v0.1) and `status`
  (v0.2). `OKF_VERSION` in the script is the one place the version is written.
- **Non-concept Markdown inside a bundle breaks conformance** (OKF issue #58).
  That is why the config and `ON_*.md` files live outside every bundle.

## When v0.3 appears

Read its change list for anything touching `type`, `description`, `status`,
`index.md`, `okf_version`, or link forms. Update `OKF_VERSION`, the docs page,
and the timeline there.

## Sources

- Karpathy, LLM Wiki:
  <https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f>
- Google Cloud, v0.1 announcement:
  <https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing>
- Google Cloud, v0.2 announcement:
  <https://cloud.google.com/blog/products/data-analytics/okf-v0-2-adds-trust-signals>
- Specification:
  <https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md>
- Move to a neutral org:
  <https://github.com/GoogleCloudPlatform/open-knowledge-format/pull/63>
