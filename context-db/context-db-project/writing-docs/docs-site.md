---
type: Reference
description:
  How the docs site is built and deployed (Sphinx, PyData theme, MyST Markdown,
  sphinx-design, GitHub Actions to Pages), what the owner requires of its pages
  (OKF up front, the install prompt first, one-word Title Case navigation, no
  Why or migration page, light mode), and the theme details that break silently.
---

# The docs site

Sources are Markdown in `docs/`. [conf.py](../../../docs/conf.py) loads MyST,
sphinx-design, and sphinx-copybutton on the PyData theme. The look comes from
[custom.css](../../../docs/_static/custom.css).

```bash
.venv/bin/sphinx-build -W docs docs/_build/html
```

`-W` makes warnings fail the build. CI runs the same command and
[docs.yml](../../../.github/workflows/docs.yml) deploys to GitHub Pages on every
push to `v0.1`.

## What the owner requires of the content

- The head of the home page and of the README must say that context-db is built
  on the Open Knowledge Format.
- Early on both, there must be a link to the explainer page,
  [docs/okf.md](../../../docs/okf.md). That page covers what OKF is, a short
  history with a hyperlink for every entry, and which parts context-db uses.
- Both must say plainly that context-db is a set of skills.
- The theme should be colorful, "a bit snazzier than usual". Pages open in
  light mode; the owner asked for "white docs".

Added by the owner on 2026-11-11:

- The home page, the README, and the Setup page lead with the prompt a user
  pastes into their agent to install context-db from the GitHub repository.
  People must be able to point their agent at the repository and have it do the
  setup.
- Labels in the top navigation are Title Case, and one word where possible.
  "Get started" and "Knowledge base" were rejected; they became Setup and
  Layout.
- There is no page for "why" and none for migrating from v0.0. The why is a
  short section at the end of the home page and the README. Migration is the
  owner's own task; its guide stays in this knowledge base and out of the docs.
- On the Commands page, each command's section is headed by the full command,
  such as `/context-db update`.

Follow [voice.md](./voice.md) for every page.

## Things that break silently

- The install prompt sends an agent to the README on GitHub. The README's
  Install section must stay a set of steps an agent can follow alone, ending
  with `configure` run through the script.
- The gradient title on the home page is selected by `section#context-db > h1`.
  That id comes from the page title. Change the title and the styling is lost.
- Definition lists need `deflist` in `myst_enable_extensions`. Without it they
  render as plain paragraphs and the build still passes.
- Dropdown colors come from `:color: secondary` on the directive, not from CSS.
- Every page is top level, so `html_sidebars` is emptied. A page added inside a
  subfolder needs that revisited.
- Link colors are set per theme in `custom.css`. Check a new color in both light
  and dark mode.
- `docs/_static/og-image.png` is rendered from `og-image.svg` with a headless
  browser at 1200 by 630. Re-render it after editing the SVG.

## Checking a change

Build, then look at the page. A headless Chromium through Playwright works in a
codespace after `playwright install chromium` and `playwright install-deps`.
Screenshot light and dark mode, and a phone width.
