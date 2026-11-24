# How to Check the Usage Folders

The usage folders ({usage_list}) hold usage knowledge: the bare minimum that
an agent working in another project needs to know to use this one. Those
projects mount a usage folder, or list it as global context, so its reader
may never have seen this repository.

Go through each one the way context-db Maintain says, for that reader: one
who uses this project and does not read its insides. This is what changes:

- **Repeats the project** means what the project already tells its users: its
  README, its docs, the definition of its API, its help text, its examples. A
  reprinted API, a schema, a list of commands or flags, or a configuration
  reference goes. Say where it is instead, and keep only what it leaves out.
- **Project knowledge** does not belong: why the project is built the way it
  is, its own conventions, how to change it, its plans. If the next agent
  working on this project would need it, move it to the project folder.
  Otherwise delete it.
- **Wrong** is judged by the project as it is now. Fix every path or URL that
  no longer leads anywhere, and delete what is about a part of the project
  that is gone.
- **Does not stand alone.** "This project" and "here" mean something else to
  a reader in another repository: use the project's name. A link that leaves
  its usage folder becomes a URL, or the project's name and the path from the
  top of its repository.
- **Duplicated** includes the same thing in two usage folders. Keep it in the
  one whose readers need it.
- **Vague descriptions.** The one in a usage folder's own descriptor matters
  most. It is all an agent in another project sees before deciding whether to
  look inside.
- **Not worth keeping.** Ask of each note: if it were deleted, would an agent
  in another project use this one wrongly, or fail to use it? If not, it
  goes.
