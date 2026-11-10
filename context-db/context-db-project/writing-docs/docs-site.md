---
type: Reference
description:
  How the docs site is built and deployed (Sphinx, PyData theme, MyST Markdown,
  sphinx-design, GitHub Actions to Pages), what the home page and README must
  say about OKF, and the theme details that break silently when pages are
  renamed.
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
- The theme should be colorful, "a bit snazzier than usual".

Follow [voice.md](./voice.md) for every page.

## Things that break silently

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
