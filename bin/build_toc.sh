#!/usr/bin/env bash
#
# build_toc.sh — Generate <folder>_toc.md files for context directories.
#
# A context node is any directory containing a recognized description file:
#   <foldername>.md, SKILL.md, CONTEXT.md, AGENT.md, or AGENTS.md
#
# The description file must have YAML front matter with a `description` key.
# The script reads that description and builds a _toc.md index for each node.
#
# Rules:
#   - Underscore-prefixed and dot-prefixed names are always skipped
#   - Symlinked folders appear in the parent TOC but are never written into
#   - Only writes _toc.md files whose real path is under the project root
#
# Usage:
#   bin/build_toc.sh                   Rebuild changed TOC files
#   bin/build_toc.sh --build-all       Rebuild all TOC files unconditionally
#   bin/build_toc.sh CONTEXT/          Build from a specific directory
#
# Requirements: bash 3.2+, awk, stat, find

set -eo pipefail

BUILD_ALL=false
DESC_NAMES="SKILL.md CONTEXT.md AGENT.md AGENTS.md"

# ── Parsing ───────────────────────────────────────────────────────────────────

# Read description — tries YAML front matter first, then fenced ```yaml description```
read_desc() {
    local desc
    desc=$(awk '
        /^---$/ { fc++; next }
        fc == 1 && /^description:/ {
            sub(/^description:[[:space:]]*/, "")
            gsub(/^["'"'"']|["'"'"']$/, "")
            print; exit
        }
        fc >= 2 { exit }
    ' "$1")
    [ -z "$desc" ] && desc=$(awk '
        /^```yaml description/ { in_b=1; next }
        in_b && /^```/ { exit }
        in_b && /^description:/ {
            sub(/^description:[[:space:]]*/, "")
            gsub(/^["'"'"']|["'"'"']$/, "")
            print; exit
        }
    ' "$1")
    echo "$desc"
}

# Find the description file for a directory (returns path or fails)
find_desc_file() {
    local dir="$1" name
    name=$(basename "$dir")
    [ -f "$dir/${name}.md" ] && { echo "$dir/${name}.md"; return 0; }
    local f
    for f in $DESC_NAMES; do
        [ -f "$dir/$f" ] && { echo "$dir/$f"; return 0; }
    done
    return 1
}

# ── Helpers ───────────────────────────────────────────────────────────────────

should_skip() {
    case "$1" in _*|.*) return 0 ;; esac
    return 1
}

file_mtime() {
    stat -f %m "$1" 2>/dev/null || stat -c %Y "$1" 2>/dev/null
}

needs_rebuild() {
    local dir="$1" toc_file="$2"
    [ ! -f "$toc_file" ] && return 0

    local toc_mt
    toc_mt=$(file_mtime "$toc_file")

    for f in "$dir"/*.md; do
        [ -f "$f" ] || continue
        [ "$(file_mtime "$f")" -gt "$toc_mt" ] && return 0
    done

    local sub_desc
    for subdir in "$dir"/*/; do
        [ -d "$subdir" ] || continue
        sub_desc=$(find_desc_file "$subdir" 2>/dev/null) || continue
        [ "$(file_mtime "$sub_desc")" -gt "$toc_mt" ] && return 0
    done

    return 1
}

# ── Build one directory ───────────────────────────────────────────────────────

build_dir() {
    local dir="$1"
    local foldername desc_file toc_file description
    foldername=$(basename "$dir")
    desc_file=$(find_desc_file "$dir") || return 0
    toc_file="$dir/${foldername}_toc.md"
    description=$(read_desc "$desc_file")

    local desc_fname
    desc_fname=$(basename "$desc_file")

    echo "  Building: $toc_file"

    # Folder entries
    local folder_lines=""
    for subdir in "$dir"/*/; do
        [ -d "$subdir" ] || continue
        local subname=$(basename "$subdir")
        should_skip "$subname" && continue

        local sub_desc
        sub_desc=$(find_desc_file "$subdir") || continue

        local sdesc
        sdesc=$(read_desc "$sub_desc")
        [ -z "$sdesc" ] && sdesc="(no description)"
        folder_lines="${folder_lines}"$'\n'"- description: ${sdesc}"$'\n'"  path: ${subname}/${subname}_toc.md"
    done

    # File entries (skip the description file and the toc file)
    local file_lines=""
    for md_file in "$dir"/*.md; do
        [ -f "$md_file" ] || continue
        local fname=$(basename "$md_file")
        [ "$fname" = "$desc_fname" ] && continue
        [ "$fname" = "${foldername}_toc.md" ] && continue
        should_skip "$fname" && continue

        local fdesc
        fdesc=$(read_desc "$md_file")
        [ -z "$fdesc" ] && fdesc="(no description)"

        file_lines="${file_lines}"$'\n'"- description: ${fdesc}"$'\n'"  path: ${fname}"
    done

    # Write
    {
        if [ -n "$folder_lines" ]; then
            printf '%s\n%s\n' "## Subfolders" "$folder_lines"
        fi
        if [ -n "$file_lines" ]; then
            [ -n "$folder_lines" ] && printf '\n'
            printf '%s\n%s\n' "## Files" "$file_lines"
        fi
    } > "$toc_file"
}

# ── Recursive walk ────────────────────────────────────────────────────────────

walk() {
    local dir="$1"
    local project_root="$2"
    local foldername
    foldername=$(basename "$dir")

    find_desc_file "$dir" >/dev/null 2>&1 || return 0

    # Only write if real path is under project root
    local real_dir
    real_dir=$(cd "$dir" && pwd -P)
    case "$real_dir" in
        "$project_root"|"${project_root}"/*)
            local toc_file="$dir/${foldername}_toc.md"
            if $BUILD_ALL || needs_rebuild "$dir" "$toc_file"; then
                build_dir "$dir"
            fi
            ;;
        *)
            echo "  Skipping (outside project): $dir"
            ;;
    esac

    # Recurse into subdirectories (never into symlinks)
    for subdir in "$dir"/*/; do
        [ -d "$subdir" ] || continue
        local subname=$(basename "$subdir")
        should_skip "$subname" && continue
        [ -L "${subdir%/}" ] && continue

        walk "$subdir" "$project_root"
    done
}

# ── Main ──────────────────────────────────────────────────────────────────────

main() {
    while [ $# -gt 0 ]; do
        case "$1" in
            --build-all) BUILD_ALL=true; shift ;;
            *) break ;;
        esac
    done

    local project_root
    project_root=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
    project_root=$(cd "$project_root" && pwd -P)

    echo "context-md: building TOC files..."

    if [ $# -eq 0 ]; then
        # Find root context nodes: dirs with a desc file whose parent has none
        find "$project_root" -name "*.md" \
             -not -name "*_toc.md" \
             -not -path "*/.git/*" \
             -not -path "*/node_modules/*" \
             | sort \
             | while IFS= read -r f; do
            local d=$(dirname "$f")
            local base=$(basename "$f" .md)
            local dname=$(basename "$d")

            # Must be a recognized description file for this directory
            if [ "$base" != "$dname" ]; then
                case "$base" in SKILL|CONTEXT|AGENT|AGENTS) ;; *) continue ;; esac
            fi

            # Skip if parent is also a context node (not a root)
            local parent=$(dirname "$d")
            find_desc_file "$parent" >/dev/null 2>&1 && continue

            walk "$d" "$project_root"
        done

    elif [ -d "$1" ]; then
        walk "$(cd "$1" && pwd)" "$project_root"

    elif [ -f "$1" ]; then
        walk "$(cd "$(dirname "$1")" && pwd)" "$project_root"

    else
        echo "Error: '$1' is not a file or directory" >&2
        exit 1
    fi

    echo "Done."
}

main "$@"
