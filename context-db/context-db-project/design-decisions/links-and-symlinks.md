---
type: Decision
description:
  Why links are file-relative Markdown links, why symlinks are allowed only at
  the top level of context-db/, and why a mounted bundle may not link outside
  itself — together these removed the v0.0 path resolver script
---

# Links and symlinks

## Links are real Markdown links, relative to the containing file

`[retry policy](./retry-policy.md)`, never a backticked path and never a link
starting with `/`.

- A bundle can be mounted under a different path or name in another project.
  Only file-relative links travel with the content.
- OKF recommends bundle-relative links (`/tables/x.md`), but those resolve
  against the repository root on GitHub and in Sphinx, so they break whenever a
  bundle is a subdirectory. File-relative links are also valid OKF.
- A real link is a graph edge that lint can check and OKF tools can follow. A
  backticked path is neither.

## Symlinks only at the top level

A symlink is how a background bundle gets mounted. Inside a bundle a symlink is
a lint error. This is what makes committed `index.md` files safe; see
[static-index.md](./static-index.md).

## A mounted bundle never links outside itself

The kernel resolves a symlink before walking `..`, while tools that normalize
paths textually do the opposite. v0.0 shipped a resolver script and told agents
to run it on every `..` link. v0.1 removes the ambiguity instead: a link that
stays inside its own bundle resolves the same both ways, so a bundle meant to be
shared must be self-contained.

The project bundle may link out, to code or to a background bundle, because it
is never the symlinked one.

## Commands never edit a background bundle

It belongs to another repository. Edits made through the symlink would land in
that repo's working tree unreviewed.
