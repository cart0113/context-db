"""Entry point of the `context-db` command that pyproject.toml installs.

The script keeps its hyphenated name, because the skill is copied into projects as it
is and its docs name it, so it cannot be imported as a module. This runs it by path.
Copying the skill folder into a project does not need this file.
"""

import importlib.util
import os


def main():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "context-db.py")
    spec = importlib.util.spec_from_file_location("context_db_script", path)
    script = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(script)
    script.main()


if __name__ == "__main__":
    main()
