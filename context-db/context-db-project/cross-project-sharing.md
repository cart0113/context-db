---
description:
  Share context-db folders across projects — committed for the team, symlinked
  for yourself, or pulled via git-sync/submodule
---

# Cross-Project Sharing

A context-db often contains knowledge useful to multiple projects — coding
standards, domain context, shared conventions. You can share context-db folders
across projects at three levels of visibility, and mix them freely.

## How It Works

Every approach ends the same way: a folder appears inside your `context-db/`
directory, and `bin/show_toc.sh` picks it up automatically. The difference is
how that folder gets there and who else sees it.

Because `show_toc.sh` generates the TOC on the fly, there are no static files to
get out of sync. If you symlink in a private folder and `.gitignore` it, your
agent sees it in the TOC but nothing changes in git. Other users' agents see
only their own folders.

## Committed Folders (Whole Team)

The simplest case: put the folder directly in `context-db/` and commit it. Every
clone gets it. This is the default for project-specific knowledge.

```
your-project/
  context-db/
    your-project/        # committed — everyone sees this
      architecture.md
      data-model/
```

## Symlink + .gitignore (Just You)

Symlink a folder from another local project and `.gitignore` the symlink. Only
your agent sees it.

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
isn't there for them. No broken references, no dirty working tree.

**Best for:** Personal reference context. Quick access to another project's
knowledge without any setup for the team.

## Git Submodule (Team, Pinned)

Add the external repo as a git submodule. Every clone gets it.

```bash
git submodule add https://github.com/org/standards.git external/standards
cd context-db
ln -s ../external/standards/context-db/coding-standards coding-standards
```

Both the submodule and the symlink are committed. The content is pinned to a
specific commit and updated explicitly with `git submodule update --remote`.

**Best for:** Shared external context the whole team should see, when you want
git-native tooling and explicit version pinning.

## Git-Sync (Flexible, Sparse, Private or Shared)

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

Git-sync hooks auto-pull on `git pull`, so external context stays current.

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

## Mixing Approaches

These approaches compose. A typical setup might look like:

```
context-db/
  my-project/              # committed — project knowledge
  coding-standards/        # submodule — org-wide standards
  personal-notes/          # symlink + .gitignore — just for you
```

`bin/show_toc.sh context-db/` shows all three. Each teammate sees committed
folders plus whatever they've symlinked in locally.
