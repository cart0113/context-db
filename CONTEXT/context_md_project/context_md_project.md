---
description: The context-md standard — design decisions and tooling
---

Key constraint: `build_toc.sh` must stay bash 3.2 compatible (macOS system bash).
Do not use associative arrays, namerefs, or other bash 4+ features.
