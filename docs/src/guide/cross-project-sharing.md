# Cross-Project Sharing

Symlink folders from other repos into your `context-db/` directory.
`show_toc.sh` generates the TOC on the fly, so symlinked folders appear
automatically.

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
