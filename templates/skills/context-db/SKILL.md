---
name: context-db
description: 'Type --help for sub-commands or <command> --help for details'
allowed-tools: Bash,Read,Write,Edit,Glob,Grep
---

python3 .claude/skills/context-db/scripts/context-db-main-agent.py <args>

Run with the user's arguments. The script uses argparse subcommands — each
subcommand accepts one positional `instruction` argument. When the user passes a
multi-word instruction, you MUST quote it as a single shell argument:

    # WRONG — argparse sees each word as a separate arg and fails:
    python3 ...main-agent.py update Make sure notes are stored

    # RIGHT — the instruction is one quoted string:
    python3 ...main-agent.py update "Make sure notes are stored"

If output contains [instructions], follow them. Otherwise print the output for
the user.
