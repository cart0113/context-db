# Cross-Project Sharing

Symlink folders from other repos into your `context-db/` directory.
`context-db-generate-toc.sh` generates the TOC on the fly, so symlinked folders
appear automatically.

**Private** — symlink + `.gitignore`. Only your agent sees it.

```bash
cd context-db
ln -s ~/workspace/OTHER_PROJECT/context-db/coding-standards coding-standards
echo "context-db/coding-standards" >> ../.gitignore
```

**Shared** — git submodule, then symlink. Every clone gets it.

```bash
git submodule add https://github.com/org/standards.git external/standards
cd context-db
ln -s ../external/standards/context-db/coding-standards coding-standards
```

**Shared (git-sync)** — [git-sync](https://github.com/cart0113/GIT_GIT_SYNC), a
lightweight alternative to git submodule. Declare dependencies in
`.git-sync.yaml` and hooks keep them current on pull.

```yaml
# .git-sync.yaml
standards:
  path: external/standards
  git-repo: https://github.com/org/standards.git
  mode: update-branch
  current-branch: main
  current-commit: abc1234
```

```bash
bin/git-sync.sh sync
cd context-db
ln -s ../external/standards/context-db/coding-standards coding-standards
```
