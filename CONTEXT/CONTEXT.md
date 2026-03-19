```yaml description
title: context-md
description: Context for the context-md project — the standard itself, design decisions, and tooling
```

This is the context-md project itself — the repository that defines the standard
and ships `bin/build_toc.sh`.

Key constraints: `build_toc.sh` must stay bash 3.2 compatible (macOS system bash).
Do not use associative arrays, namerefs, or other bash 4+ features.
