# context-db

Hierarchical Markdown knowledge base with on-demand tables of contents for LLM
agents. Agents run `bin/show_toc.sh` on a folder, see one-line descriptions of
every subfolder and file, and fetch only what's relevant. Agents write back what
they learn — architecture decisions, gotchas, non-obvious patterns — so future
agents don't rediscover the same knowledge.

## Features

- **On-demand TOCs from filesystem** -- `bin/show_toc.sh` generates tables of
  contents on the fly from YAML frontmatter. No static files to commit or keep
  in sync.
- **Progressive disclosure** -- agents browse TOCs top-down, reading
  descriptions to decide what to fetch. Scales from a handful of files to
  hundreds without flooding context.
- **Two-way knowledge** -- agents read context and write it back. The knowledge
  base stays current as the codebase evolves.
- **Cross-project sharing** -- symlink folders from other repos into
  `context-db/` and they appear in the TOC automatically. Private symlinks via
  `.gitignore`, shared via submodule or git-sync.
- **Zero dependencies** -- bash 3.2+ and awk, pre-installed on macOS and Linux.
- **Tool-agnostic** -- works with Claude Code, Codex, Cursor, or any tool that
  can run shell commands and read stdout.
- **Copy-based install** -- copy `templates/bin/` and `templates/context-db/`
  into your project. A sample `AGENTS.md` and `SKILLS.md` are also provided.

## How It Works

1. `AGENTS.md` points the agent to `context-db/context-db-instructions.md`
2. The instructions file teaches navigation and maintenance rules
3. The agent runs `bin/show_toc.sh context-db/` to browse the knowledge tree
4. Descriptions in YAML frontmatter let the agent skip irrelevant branches

## Quick Start

```bash
cp -r templates/bin your-project/bin
cp -r templates/context-db your-project/context-db
chmod +x your-project/bin/show_toc.sh
```

Then create your project folder and point `AGENTS.md` at the instructions file.
See the
[Getting Started](https://cart0113.github.io/context-db/#/src/guide/getting-started)
guide.

## Structure

```
templates/              Copy these into your project
  bin/show_toc.sh       TOC generator
  context-db/           Instructions file
  AGENTS.md             Sample agent config section
  skills/context-db/    Sample SKILLS.md for Claude Code
bin/show_toc.sh         Canonical TOC generator
context-db/             This project's own knowledge database
example/                Example project structure
docs/                   GitHub Pages documentation
```

## Documentation

Full docs: https://cart0113.github.io/context-db/

## License

MIT
