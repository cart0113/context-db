---
type: Decision
description:
  What the Open Knowledge Format (OKF) and Karpathy's LLM Wiki are, how each
  maps onto context-db, and why v0.1 adopted OKF as the file format while keeping
  context-db's own operating rules. Includes the risks of tracking a young spec.
---

# OKF: what it is and whether context-db fits

Researched 2026-11-10 from the primary sources listed at the bottom.

## Lineage

1. **April 2026 — Karpathy's "LLM Wiki" gist.** An idea file, not a standard. An
   LLM maintains a persistent wiki of interlinked Markdown instead of
   re-deriving answers from raw documents on every query (RAG).
2. **June 2026 — Google Cloud publishes OKF v0.1**, formalizing that pattern
   into a portable format. Karpathy did not write or push OKF; Google did, citing
   his pattern.
3. **July 2026 — OKF v0.2** adds provenance, trust, lifecycle, and "attested
   computations". It also made two breaking renames only six weeks after v0.1.
4. **August 2026** — the spec moves from `knowledge-catalog/okf` to
   `GoogleCloudPlatform/open-knowledge-format`.
5. **November 2026** — an open PR (#63, by a Google collaborator) deprecates that
   repo in favor of a vendor-neutral `open-knowledge-format` org where v0.3 is
   being developed. That org has no public repositories yet, so **v0.2 is the
   latest spec anyone can read**.

## Karpathy's pattern in one screen

Three layers and three operations:

| Karpathy                                 | context-db equivalent                           |
| ---------------------------------------- | ----------------------------------------------- |
| Raw sources (immutable)                  | The codebase itself, plus background folders    |
| The wiki (LLM-written Markdown)          | `context-db/<name>-project/`                    |
| The schema (`AGENTS.md` rules for the LLM) | The skill's prompts, `ON_*.md`, `AGENTS.md`     |
| Ingest                                   | `/context-db update`                            |
| Query                                    | `/context-db prompt`                            |
| Lint                                     | The lint pass in the `index` helper             |
| `index.md` (catalog read first)          | Generated `index.md` files                      |
| `log.md` (append-only history)           | Git history and `update --push` commit messages |

context-db already is this pattern. The two were built independently and
converged, which is the strongest argument that the shape is right.

## OKF in one screen

A **bundle** is a directory tree of Markdown files. Each file is a **concept**:
YAML frontmatter plus a Markdown body. The whole conformance bar is three rules:

1. Every `.md` file except the reserved names has parseable YAML frontmatter.
2. That frontmatter has a non-empty `type` (free-form string, no registry).
3. `index.md` and `log.md`, if present, follow their prescribed shape.

Everything else is optional:

- **Recommended keys**: `title`, `description`, `resource`, `tags`.
- **`index.md`** in any directory: no frontmatter, headed sections of
  `* [Title](path) - description` lines. This is "progressive disclosure".
  Consumers may synthesize one on the fly when it is absent.
- **`log.md`**: date-grouped change history, newest first.
- **Links**: ordinary Markdown links. Bundle-relative (`/tables/x.md`) is
  recommended; file-relative (`./x.md`) is allowed. Broken links are tolerated.
- **Lifecycle**: `status: draft | stable | deprecated`, and `stale_after`.
- **Trust**: `generated: {by, at}`, `verified: [{by, at}]`, from which a consumer
  derives unverified, machine-confirmed, or human-reviewed.
- **Provenance**: `sources` with per-source credibility signals.
- **Attested computations**: sanctioned SQL plus a deterministic checker.
- Unknown keys and unknown types must be tolerated by consumers.

OKF explicitly does not define storage, serving, search, or any workflow. It is
a file format and nothing more.

## How context-db v0.0 mapped

| OKF v0.2                         | context-db v0.0                      | Gap                              |
| -------------------------------- | ------------------------------------ | -------------------------------- |
| Frontmatter on every concept     | Frontmatter on every file            | None                             |
| `type` required                  | Absent                               | Add one line per file            |
| `description` recommended        | `description` required               | None (stricter)                  |
| `index.md` per directory         | TOC printed by a script              | Generate `index.md` instead      |
| Directory described in parent's index | `<folder>/<folder>.md` descriptor | Keep descriptor as a concept     |
| `status` with 3 values           | `status` with 6 values               | Trim to 3; `wip/` covers the rest |
| Markdown links, either form      | File-relative paths, often backticked | Make them real links             |
| `log.md` optional                | None                                 | Skip; git is the log             |
| Trust, provenance, attestation   | Deliberately rejected                | Skip, see below                  |

## Verdict: a fit as the format, not as the philosophy

**Adopt it.** context-db is one required key (`type`) away from conformance.
What that buys:

- A name for the format, so the project can stop specifying its own. The pitch
  becomes: _OKF says what the files look like; context-db says when a coding
  agent reads and writes them._
- Interop for free: Obsidian, OKF viewers, static site generators, and catalog
  tools can all read the bundle.
- A static `index.md` that an agent reads with its plain file-read tool, with no
  script on the read path. See [static-index.md](./static-index.md).

**What OKF does not give you** is everything that makes context-db work: the
re-injection moment, the bar for what is worth storing, the wip loop. Those stay
ours.

### Where we deliberately differ

- **Accumulate versus cut.** Karpathy's wiki compiles external sources the LLM
  cannot otherwise re-read cheaply, so more pages is better. A coding agent can
  read the code directly, and the ETH Zurich result says generated context files
  hurt. context-db keeps its rule that most sessions store nothing. Take the
  format, not the "ingest everything" ethos.
- **Trust and provenance keys.** `generated`, `verified`, `sources`, and
  `stale_after` duplicate what git blame and git log already record for an
  in-repo bundle, and unmaintained trust fields create false confidence. This is
  the same reasoning as the existing decision to reject `last-reviewed`. Do not
  write them; tolerate them if present.
- **Link form.** Keep file-relative links. OKF's recommended bundle-relative
  form breaks on GitHub, in Sphinx, and under symlinks (OKF issue #59 reports
  exactly this).
- **Data-catalog machinery.** Roughly half of v0.2 (attested computations, usage
  counts, `resource` URIs) is for BigQuery-style catalogs and is irrelevant here.

### Risks

- **The spec is young and moving.** Two breaking changes between v0.1 and v0.2,
  three repository homes in five months, and v0.3 not yet visible. Mitigation:
  depend only on the stable core (frontmatter, `type`, `description`,
  `index.md`, links, `status`), which has not changed since v0.1.
- **Non-concept Markdown inside a bundle** is non-conformant (OKF issue #58).
  Mitigation: make each top-level folder its own bundle and keep `ON_*.md` and
  the config outside any bundle.
- **Governance** is still Google-led in practice until the neutral org opens.

## Sources

- Karpathy, LLM Wiki gist:
  <https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f>
- OKF v0.2 spec:
  <https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md>
- Deprecation PR pointing at the neutral org:
  <https://github.com/GoogleCloudPlatform/open-knowledge-format/pull/63>
- OKF issues #10 (folder lead concepts), #58 (non-concept files), #59 (link form)
  in the same repository.
- Release dates for v0.1 (June 12) and v0.2 (July 24) come from secondary
  coverage, not the spec itself.
