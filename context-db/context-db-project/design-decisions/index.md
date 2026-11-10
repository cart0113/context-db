# Files

* [Config layering](config-layering.md) - Why there is a committed context-db.json plus a gitignored context-db.local.json, why the interpreter is a config value the agent reads rather than something the script resolves, and why the key set is closed
* [Frontmatter fields](frontmatter-fields.md) - Why frontmatter is limited to type, description, optional status, and branch on wip files — and why OKF's tags, trust, provenance, and timestamp keys are tolerated but never written
* [gate-before-action](gate-before-action.md) - Why write-command templates put the null-result decision before writing instructions — counters LLM action bias from RLHF
* [Links and symlinks](links-and-symlinks.md) - Why links are file-relative Markdown links, why symlinks are allowed only at the top level of context-db/, and why a mounted bundle may not link outside itself — together these removed the v0.0 path resolver script
* [Naming Convention](naming-convention.md) - Why files are named after their parent folder rather than using fixed names
* [OKF: what it is and whether context-db fits](okf-adoption.md) - What the Open Knowledge Format (OKF) and Karpathy's LLM Wiki are, how each maps onto context-db, and why v0.1 adopted OKF as the file format while keeping context-db's own operating rules. Includes the risks of tracking a young spec.
* [Python and Argparse](python-and-argparse.md) - Why all scripts are Python 3 with argparse — minimal dependency choice, why not bash, why not click
* [Static index inside a bundle, dynamic listing above it](static-index.md) - Why index.md files are generated and committed inside a bundle while the top-level bundle listing is printed on every call — reverses v0.0's fully dynamic TOC without reintroducing the per-user symlink problem
