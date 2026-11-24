# Usage Knowledge

Usage knowledge is the bare minimum that an agent working in another project
needs to know to use this one. It lives in a usage folder ({usage_list}),
which those projects mount or list as global context, so its reader may never
have seen this repository. Folders, below, describes each usage folder, or
says that it does not exist yet.

The test, for that reader: would an agent in another project use this one
wrongly, or fail to use it, without the change? Most sessions change nothing
here.

What belongs is what the project does not already tell its users: what it is
for and when to use it, where to start and where it describes its own
interface, which way in suits which job, rules that the interface does not
enforce, and mistakes its users make. Never reprint an API, a schema, a list
of commands or flags, or a configuration reference. Say where it is, and add
only what it leaves out. What only the code or its comments say does not count
as told: that reader does not read this project's insides. Project knowledge
stays in the project folder.

- Run `{toc_cmd} <folder>` on a usage folder first, to see what is already
  there. Fix what this session made untrue, and delete what the project now
  tells its users itself.
- When there are several usage folders, each is for different readers, as its
  description says. Put a note in the one whose readers need it, never the
  same thing in two, and do not start a folder that is not listed.
- Create a listed folder that does not exist yet when you have something for
  it, starting with its descriptor, which Folders names. Its description is
  all an agent in another project sees before deciding whether to look
  inside: say what this project is and what the notes cover.
- A usage folder is read from wherever it is mounted, so it must stand on its
  own. Link only to files inside it. Point at anything else by its URL, or by
  the project's name and the path from the top of its repository, as in
  "`api/openapi.yaml` in the acme-ledger repository". Call the project by its
  name, never "this project" or "here".
