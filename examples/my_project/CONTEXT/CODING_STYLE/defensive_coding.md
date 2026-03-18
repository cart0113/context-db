---
title: Defensive Coding Guidelines
description: Guidelines for writing defensive, explicit code that avoids silent failures
---

# Defensive Coding Guidelines

## Prefer Explicit Failures Over Silent Defaults

Do not use `.get()` with default fallback values on dict lookups. If a key should exist, access it directly. A `KeyError` at the exact failure point is more useful than a default value propagating silently through the system.

```python
# Bad
value = config.get("timeout", 30)

# Good
value = config["timeout"]
```

## No Fallback Branches for Expected State

Do not write `else` branches to handle states that should never occur. If the state is impossible given correct inputs, do not defend against it — let the program raise naturally.

## Required Parameters Over Defaults

Function parameters should be required unless there is a well-defined and universally applicable default. When in doubt, require it.

## Validate at System Boundaries

Validate input at the entry points to the system (HTTP handlers, CLI argument parsing, file loading). Inside the system, trust that data is well-formed.
