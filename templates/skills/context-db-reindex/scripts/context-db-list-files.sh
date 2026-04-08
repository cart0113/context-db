#!/usr/bin/env bash
#
# context-db-list-files.sh — List context-db files and folders without following symlinks.
#
# Outputs real (non-symlink) .md files and directories under the target path.
# Symlinked files and directories are skipped — they belong to other repos
# and must not be modified by reindex or audit operations.
#
# Usage:
#   context-db-list-files.sh context-db/              All real files
#   context-db-list-files.sh context-db/some-folder/   Scoped to subfolder
#
# Output format:
#   ## Folders
#   context-db/coding-standards/
#   context-db/my-project/
#
#   ## Files
#   context-db/coding-standards/coding-standards.md
#   context-db/my-project/architecture.md

set -eo pipefail

dir="${1:-.}"
dir="${dir%/}"

if [ ! -d "$dir" ]; then
    echo "Error: '$dir' is not a directory" >&2
    exit 1
fi

# Folders — real directories only, no symlinks
folder_lines=""
while IFS= read -r d; do
    [ -L "$d" ] && continue
    folder_lines="${folder_lines}${d}/
"
done < <(find "$dir" -mindepth 1 -type d ! -name '.*' ! -name '_*' | sort)

# Files — real .md files only, no symlinks
file_lines=""
while IFS= read -r f; do
    [ -L "$f" ] && continue
    file_lines="${file_lines}${f}
"
done < <(find "$dir" -mindepth 1 -type f -name '*.md' ! -name '.*' ! -name '_*' | sort)

if [ -n "$folder_lines" ]; then
    printf '## Folders\n%s' "$folder_lines"
fi
if [ -n "$file_lines" ]; then
    [ -n "$folder_lines" ] && printf '\n'
    printf '## Files\n%s' "$file_lines"
fi
