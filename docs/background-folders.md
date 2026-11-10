# Sharing knowledge between projects

Some knowledge is not about one project. Coding standards, how your team uses
git, and notes on a library are examples. Keep knowledge like that in one place
and mount it into each project that needs it.

Any folder at the top level of `context-db/`, other than the project folder, is
a background folder. `prompt` lists background folders next to the project
folder. The commands read them and never change them.

```text
context-db/
├── acme-payments-project/       this project's knowledge
├── coding-standards -> ...      shared, mounted with a symlink
└── git-standards -> ...         shared, mounted with a symlink
```

## Three rules

1. Mount a background folder at the top level of `context-db/`, and nowhere
   deeper.
2. Links inside a shared folder must stay inside it. A link that leaves the
   folder points at something that may not exist in the next project.
3. The `index.md` files of a shared folder are made in the repository that owns
   it.

## Ways to mount a folder

| Method | Who sees it | In git | How it updates |
| --- | --- | --- | --- |
| A copy | Everyone | Yes | You copy it again |
| A symlink that is gitignored | Only you | No | It follows the other repository |
| A git submodule and a symlink | Everyone | Yes, pinned | `git submodule update` |

### Only for you

```bash
cd context-db
ln -s ~/work/standards/context-db/coding-standards coding-standards
echo "context-db/coding-standards" >> ../.gitignore
```

Your agent sees the folder. Your teammates' agents do not, and nothing in git
changes. This works because the list of folders is built fresh every time
`prompt` runs.

The symlink can have a different name from the folder it points at.

### For the whole team

```bash
git submodule add https://github.com/your-org/standards.git external/standards
cd context-db
ln -s ../external/standards/context-db/coding-standards coding-standards
```

Commit the submodule and the symlink.

## Making the index for a shared folder

Go to the repository that owns the folder and run:

```bash
python3 <path-to>/context-db.py index context-db/coding-standards
```

Naming the folder means that repository needs no settings file of its own.
Commit the `index.md` files it writes.

A shared folder with no `index.md` still works. `prompt` tells the agent to list
the folder and read the descriptions at the top of each file.
