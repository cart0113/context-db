#!/usr/bin/env bash
#
# context-db-list-files.sh — List context-db files and folders, skipping
# anything that resolves outside the project.
#
# Symlinks pointing within the project root (git repo) are included normally.
# Symlinks pointing outside — or files reached through an external symlink —
# are skipped. They belong to another repo and must not be modified.
#
# Usage:
#   context-db-list-files.sh context-db/              All project-local files
#   context-db-list-files.sh context-db/some-folder/   Scoped to subfolder
#
# Output format:
#   ## Folders
#   context-db/coding-standards/
#
#   ## Files
#   context-db/coding-standards/coding-standards.md

set -eo pipefail

dir="${1:-.}"
dir="${dir%/}"

if [ ! -d "$dir" ]; then
    echo "Error: '$dir' is not a directory" >&2
    exit 1
fi

# Determine project root
project_root="$(git rev-parse --show-toplevel 2>/dev/null || pwd -P)"
project_root="$(cd "$project_root" && pwd -P)"

# Check whether a path's real location is inside the project.
# Resolves the full path (including symlinked parents) and checks the result.
is_project_local() {
    local real
    real="$(python3 -c "import os,sys; print(os.path.realpath(sys.argv[1]))" "$1" 2>/dev/null)" || return 1
    case "$real" in
        "$project_root"/*) return 0 ;;
        *) return 1 ;;
    esac
}

# Use find -P (never follow symlinks) to get all entries, then resolve each
# one ourselves. This avoids find walking into external symlinked trees.
folder_lines=""
while IFS= read -r d; do
    is_project_local "$d" || continue
    folder_lines="${folder_lines}${d}/
"
done < <(find -P "$dir" -mindepth 1 -type d ! -name '.*' ! -name '_*' | sort)

# Symlinked directories that resolve inside the project — include them and
# let find -P discover their children in the file pass below
while IFS= read -r d; do
    [ -d "$d" ] || continue
    is_project_local "$d" || continue
    folder_lines="${folder_lines}${d}/
"
done < <(find -P "$dir" -mindepth 1 -type l ! -name '.*' ! -name '_*' | sort)

# Files — .md only. Walk real dirs and project-local symlinked dirs.
file_lines=""
# Collect all project-local directories (real + symlinked) to search
all_dirs=("$dir")
while IFS= read -r d; do
    is_project_local "$d" || continue
    all_dirs+=("$d")
done < <(find -P "$dir" -mindepth 1 \( -type d -o -type l \) ! -name '.*' ! -name '_*' | sort)

# For each directory, list immediate .md files (no recursion into subdirs —
# we handle that via the dir list above to avoid re-entering external symlinks)
for search_dir in "${all_dirs[@]}"; do
    [ -d "$search_dir" ] || continue
    for f in "$search_dir"/*.md; do
        [ -e "$f" ] || continue
        is_project_local "$f" || continue
        file_lines="${file_lines}${f}
"
    done
done

# Deduplicate and sort
folder_lines="$(echo "$folder_lines" | awk 'NF && !seen[$0]++' | sort)"
file_lines="$(echo "$file_lines" | awk 'NF && !seen[$0]++' | sort)"

if [ -n "$folder_lines" ]; then
    printf '## Folders\n%s\n' "$folder_lines"
fi
if [ -n "$file_lines" ]; then
    [ -n "$folder_lines" ] && printf '\n'
    printf '## Files\n%s\n' "$file_lines"
fi
