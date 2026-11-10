# Background bundles

`context-db/<name>-project/` is the project bundle: knowledge specific to one
repository, and the only place commands write.

Every other folder at the top level of `context-db/` is a background bundle:
coding standards, writing conventions, notes on a library. It is knowledge that
is not specific to the project and usually lives somewhere else. `prompt` lists
background bundles beside the project bundle; nothing ever edits them.

## Rules

- Mount a background bundle only at the top level of `context-db/`.
- A bundle meant for sharing links only within itself.
- Its `index.md` files are generated in the repository that owns it:

  ```bash
  python3 .claude/skills/context-db/context-db.py index context-db/coding-standards
  ```

  Passing the bundle path means that repository needs no config of its own.

A background folder with no `index.md` still works. `prompt` tells the agent to
list the folder and read frontmatter instead.

## Ways to mount

| Method               | Who sees it  | In git                        | Updates                |
| -------------------- | ------------ | ----------------------------- | ---------------------- |
| Committed copy       | Everyone     | Yes                           | Re-copy                |
| Symlink + .gitignore | Only you     | No                            | Follows the other repo |
| Submodule + symlink  | Everyone     | Yes, pinned                   | `git submodule update` |
| git-sync + symlink   | Configurable | Shared config yes, private no | `git-sync sync`        |

### A private mount

```bash
cd context-db
ln -s ~/work/standards/context-db/coding-standards coding-standards
echo "context-db/coding-standards" >> ../.gitignore
```

The list of bundles is generated on every `prompt`, so your agent sees the
symlink and a teammate's does not, and no committed file changes. The symlink
may have a different name than the folder it points at.

### A pinned mount for the team

```bash
git submodule add https://github.com/org/standards.git external/standards
cd context-db
ln -s ../external/standards/context-db/coding-standards coding-standards
```

Commit both the submodule and the symlink.

[git-sync](https://github.com/cart0113/GIT_GIT_SYNC) does the same with sparse
checkout and separate shared and private configs.
