---
type: Reference
description:
  How the docs site is built and deployed (Sphinx, PyData theme, MyST Markdown,
  sphinx-design, GitHub Actions to Pages), what the owner requires of its pages
  (OKF up front, the install prompt first, one-word Title Case navigation, no
  Why or migration page, no logo, no call-to-action buttons, light mode), how a
  look is chosen with the look picker, and the theme details that break
  silently.
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
- The home page opens with a short Example of `prompt` and `update --push`,
  before Install. It is static; the owner asked for "not animated".
- Sharing is a section of the Layout page, not a page of its own.
- No logo in the header. The name there and the home page title both read
  `/context-db`.
- No call-to-action buttons under the intro. The owner found the two pill
  buttons "really tired, very much what agents look like". The intro's own link
  to the OKF page and the Install section do that job.
- The footer keeps the theme's standard Sphinx and PyData credits.

Follow [voice.md](./voice.md) for every page.

## The look is the owner's choice

Every part of the look in `custom.css` was picked by the owner from options
tried on the real pages: the colors, the moving title, the backdrop, code blocks
as windows, the see-through header, monospace headings, the pill for the current
page. Do not restyle any of it unless asked.

The owner chooses by trying, not from a description. Put the options in the look
picker, [docs/looks/](../../../docs/looks/looks.js), which is off unless the
docs are built with `CONTEXT_DB_LOOKS=1` ([conf.py](../../../docs/conf.py)). To
have it on the published site, set that variable in `docs.yml` for as long as
the choosing takes. The owner clicks through the options and pastes back the
line the panel gives, such as `Looks: cards=stripe extras=codeglow`. Move the
chosen rules into `custom.css` and take them out of the picker. Ideas that were
tried and not adopted stay in the picker for later.

## Things that break silently

- The install prompt sends an agent to the README on GitHub. The README's
  Install section must stay a set of steps an agent can follow alone, ending
  with `configure` run through the script.
- The gradient title on the home page is selected by `section#context-db > h1`.
  That id comes from the page title. Change the title and the styling is lost.
- Definition lists need `deflist` in `myst_enable_extensions`. Without it they
  render as plain paragraphs and the build still passes.
- Dropdown colors come from `:color: secondary` on the directive. The theme
  hard-codes the tint behind it, so `custom.css` points `--sd-color-secondary-bg`
  at the palette.
- The theme's own card rule, `.bd-content .sd-card`, outranks a single class,
  and the card body paints its own background. A border, shadow, or background
  on `.command-card` does nothing unless the selector starts with `.bd-content`.
  A top stripe sat in the CSS for days without ever showing.
- Every page is top level, so `html_sidebars` is emptied. A page added inside a
  subfolder needs that revisited.
- Link colors are set per theme in `custom.css`. Check a new color in both light
  and dark mode.
- `docs/_static/og-image.png` is rendered from `og-image.svg` with a headless
  browser at 1200 by 630. Re-render it after editing the SVG. Put the SVG inline
  in a page that loads JetBrains Mono; opened as a bare image it cannot load the
  font, and the title falls back to another one.

## Checking a change

Build, then look at the page. A headless Chromium through Playwright works in a
codespace after `playwright install chromium` and `playwright install-deps`.
Screenshot light and dark mode, and a phone width.

On 2026-11-11 the owner did not see changes that had only been built locally,
and asked for them to be made visible. Take it that the owner looks at the
published site: a docs change is not seen until it is pushed.
