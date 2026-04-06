# Cross-Project Sharing

A context-db often contains knowledge useful to multiple projects — coding
standards, domain context, shared conventions. You can share context-db folders
across projects at different levels of visibility, and mix them freely.

Every approach ends the same way: a folder appears inside your `context-db/`
directory, and `bin/show_toc.sh` picks it up automatically. The difference is
how that folder gets there and who else sees it.

Because `show_toc.sh` generates the TOC on the fly, there are no static files to
get out of sync. If you symlink in a private folder and `.gitignore` it, your
agent sees it in the TOC but nothing changes in git. Other users' agents see
only their own folders.

## Private symlink + .gitignore

This is the simplest cross-project pattern. Symlink a folder from another local
repo and `.gitignore` the symlink. Only your agent sees it — nothing changes in
git for anyone else.

```bash
cd context-db
ln -s ~/workspace/OTHER_PROJECT/context-db/coding-standards coding-standards
```

```gitignore
# .gitignore
context-db/coding-standards
```

Your agent runs `bin/show_toc.sh context-db/` and sees `coding-standards/` in
the TOC. A teammate's agent does the same and doesn't — because the symlink
doesn't exist on their machine. No broken references, no dirty working tree.

**Why this matters:** The dynamic TOC is what makes this work cleanly. If TOC
files were static and committed, you'd have to choose between committing a TOC
that references folders others don't have (broken for them) or excluding your
private folders from the TOC (invisible to your agent). With `show_toc.sh`, the
TOC reflects whatever is actually present on disk.

**Best for:** Personal reference context. Quick access to another project's
knowledge without any setup for the team.

## Committed folders

The simplest case: put the folder directly in `context-db/` and commit it. Every
clone gets it. This is the default for project-specific knowledge.

```
your-project/
  context-db/
    your-project/        # committed — everyone sees this
      architecture.md
      data-model/
```

## Git submodule

Add the external repo as a git submodule, then symlink its context-db content
into yours. Every clone gets it, pinned to a specific commit.

```bash
git submodule add https://github.com/org/standards.git external/standards
cd context-db
ln -s ../external/standards/context-db/coding-standards coding-standards
```

Both the submodule and the symlink are committed. The content is pinned to a
specific commit and updated explicitly with `git submodule update --remote`.

You can use sparse checkout to pull only the `context-db/` subfolder if the
external repo is large:

```bash
git submodule add --no-checkout https://github.com/org/standards.git external/standards
cd external/standards
git sparse-checkout init --cone
git sparse-checkout set context-db/coding-standards
git checkout
```

**Best for:** Shared external context the whole team should see, when you want
git-native tooling and explicit version pinning.

## Git-sync

[git-sync](https://github.com/cart0113/GIT_GIT_SYNC) manages external repo
dependencies via YAML config. It supports sparse checkout (pull only the
`context-db/` subfolder), read-only mode, and separate private config.

**Shared config** (`.git-sync.yaml`, committed — whole team):

```yaml
standards:
  path: external/standards
  git-repo: https://github.com/org/standards.git
  read-only: true
  sparse-paths:
    - context-db/coding-standards/
```

**Private config** (`.git-sync-private.yaml`, gitignored — just you):

```yaml
my-notes:
  path: external/my-notes
  git-repo: https://github.com/me/my-notes.git
  read-only: true
  sparse-paths:
    - context-db/
```

Then symlink into `context-db/` and `.gitignore` private paths:

```bash
cd context-db
ln -s ../external/standards/context-db/coding-standards coding-standards
ln -s ../external/my-notes/context-db/research research
```

Git-sync hooks auto-pull on `git pull`, so external context stays current
without manual steps.

**Best for:** Projects that need a mix of shared and private external context,
or where you only want a subset of the external repo.

## Comparison

|                      | Committed  | Symlink + .gitignore | Submodule              | Git-Sync                      |
| -------------------- | ---------- | -------------------- | ---------------------- | ----------------------------- |
| **Who sees it**      | Everyone   | Only you             | Everyone               | Configurable                  |
| **In git**           | Yes        | No                   | Yes                    | Shared config yes, private no |
| **Sparse checkout**  | N/A        | N/A                  | Manual                 | Built-in                      |
| **Extra tooling**    | None       | None                 | None                   | git-sync                      |
| **Update mechanism** | `git pull` | Manual               | `git submodule update` | `git-sync sync` / hooks       |

## Mixing approaches

These approaches compose. A typical setup:

```
context-db/
  my-project/              # committed — project knowledge
  coding-standards/        # submodule — org-wide standards
  personal-notes/          # symlink + .gitignore — just for you
```

`bin/show_toc.sh context-db/` shows all three. Each teammate sees committed
folders plus whatever they've symlinked in locally.
