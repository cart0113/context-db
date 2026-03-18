---
title: Project Overview
description: High-level description of what my_project does and its main components
---

# my_project — Overview

`my_project` is a demo project used to illustrate how context-md works in practice.

## Components

- **api_module/** — Handles all external API interactions
- **core/** — Business logic and domain models
- **cli/** — Command-line interface

## Key Design Decisions

- All external calls go through `api_module/` — no direct HTTP calls from `core/`
- Domain models are plain data classes with no framework dependencies

## Related Context

- For coding conventions, see `CODING_STYLE/`
- For API-specific context, see `../api_module/CONTEXT/`
