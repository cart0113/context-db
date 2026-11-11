# Files

* [Include agent-facing text, never paraphrase it](auto-generated-pages.md) - Docs that show agent-facing text include the prompt files verbatim with literalinclude instead of paraphrasing them, so the docs cannot drift from what the agent actually reads.
* [The docs site](docs-site.md) - How the docs site is built and deployed (Sphinx, PyData theme, MyST Markdown, sphinx-design, GitHub Actions to Pages), what the owner requires of its pages (OKF up front, the install prompt first, one-word Title Case navigation, no Why or migration page, light mode), and the theme details that break silently.
* [README, docs home page, agent overview](sync-overview-readme.md) - README and docs/index.md tell the same story and are updated together; the agent-facing overview.md is small, independent, and never a copy of either.
* [Voice](voice.md) - How the docs and README must read — plain, clear, simple, not AI-sounding; no first person; the words to use (project folder, background folder, skills); how to show a command in an example (instruction on a new line, never in quotes). Owner feedback from 2026-11-10 and what it means in practice.
