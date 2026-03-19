#!/usr/bin/env bash
#
# build_toc.sh — Generate <folder>_toc.md files by recursively walking
#                context directories.
#
# For each directory containing <foldername>.md, builds a <foldername>_toc.md
# from the description block and front matter of context resources.
#
# Walk rules:
#   - Recurses into all subdirectories that have <subdirname>.md
#   - Skips underscore-prefixed and dot-prefixed names
#   - Skips names in the parent's `ignore` config list
#   - Skips symlinks unless they appear in the parent's `follow_symlinks` list
#   - Only writes _toc.md files whose real path is under the project root
#
# Usage:
#   bin/build_toc.sh                   Build all context nodes
#   bin/build_toc.sh --check           Only rebuild if sources changed
#   bin/build_toc.sh CONTEXT/          Build from a specific directory
#
# Requirements: bash 3.2+, awk, stat, find

set -eo pipefail

CHECK_MODE=false

# ── Parsing ───────────────────────────────────────────────────────────────────

fenced_val() {
    local val
    val=$(awk -v block="$2" -v k="$3" '
        $0 ~ ("^```yaml " block) { in_b=1; next }
        in_b && /^```/ { exit }
        in_b && $0 ~ ("^" k ":") {
            sub("^" k ":[[:space:]]*", "")
            gsub(/^["'"'"']|["'"'"']$/, "")
            print; exit
        }
    ' "$1")
    echo "${val:-$4}"
}

fenced_list_str() {
    awk -v block="$2" -v k="$3" '
        $0 ~ ("^```yaml " block) { in_b=1; next }
        in_b && /^```/ { exit }
        in_b && $0 ~ ("^" k ":[[:space:]]*\\[") {
            sub("^" k ":[[:space:]]*\\[", "")
            sub("\\].*$", "")
            n = split($0, parts, ",")
            for (i=1; i<=n; i++) {
                gsub(/^[[:space:]]+|[[:space:]]+$/, "", parts[i])
                if (parts[i] != "") printf "%s:", parts[i]
            }
            exit
        }
        in_b && $0 ~ ("^" k ":") { in_list=1; next }
        in_b && in_list && /^[[:space:]]+-/ {
            item=$0; sub(/^[[:space:]]+-[[:space:]]*/, "", item)
            gsub(/^["'"'"']|["'"'"']$/, "", item)
            if (item != "") printf "%s:", item
        }
        in_b && in_list && /^[^[:space:]]/ { exit }
    ' "$1" | sed 's/:$//'
}

fm_field() {
    awk -v f="$2" '
        /^---$/ { fc++; next }
        fc == 1 && $0 ~ ("^" f ":") {
            sub("^" f ":[[:space:]]*", "")
            gsub(/^["'"'"']|["'"'"']$/, "")
            print; exit
        }
        fc >= 2 { exit }
    ' "$1"
}

# ── Helpers ───────────────────────────────────────────────────────────────────

in_str_list() {
    local name="$1" list="$2"
    [ -z "$list" ] && return 1
    IFS=':' read -ra _items <<< "$list"
    for item in "${_items[@]}"; do
        [ "${item%/}" = "$name" ] && return 0
    done
    return 1
}

should_skip() {
    local name="$1" ignore_str="$2"
    case "$name" in _*|.*) return 0 ;; esac
    [ -n "$ignore_str" ] && in_str_list "$name" "$ignore_str" && return 0
    return 1
}

# ── Change detection ──────────────────────────────────────────────────────────

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

    for subdir in "$dir"/*/; do
        [ -d "$subdir" ] || continue
        local subname=$(basename "$subdir")
        local sub_desc="$subdir/${subname}.md"
        [ -f "$sub_desc" ] && [ "$(file_mtime "$sub_desc")" -gt "$toc_mt" ] && return 0
    done

    return 1
}

# ── Build one directory ───────────────────────────────────────────────────────

build_dir() {
    local dir="$1"
    local foldername=$(basename "$dir")
    local desc_file="$dir/${foldername}.md"
    local toc_file="$dir/${foldername}_toc.md"

    local title description ignore_str
    title=$(fenced_val       "$desc_file" "description" "title"       "(untitled)")
    description=$(fenced_val "$desc_file" "description" "description" "")
    ignore_str=$(fenced_list_str "$desc_file" "config" "ignore")

    echo "  Building: $toc_file"

    # Folder entries
    local folder_lines=""
    for subdir in "$dir"/*/; do
        [ -d "$subdir" ] || continue
        local subname=$(basename "$subdir")
        should_skip "$subname" "$ignore_str" && continue
        local sub_desc="$subdir/${subname}.md"
        [ -f "$sub_desc" ] || continue

        local sdesc ro_flag=""
        sdesc="$(fenced_val "$sub_desc" "description" "description" "(no description)")"
        [ -L "${subdir%/}" ] && ro_flag=" *(read-only)*"

        folder_lines="${folder_lines}"$'\n'"| [${subname}/](${subname}/${subname}_toc.md) | ${sdesc}${ro_flag} |"
    done

    # File entries
    local file_lines=""
    for md_file in "$dir"/*.md; do
        [ -f "$md_file" ] || continue
        local fname=$(basename "$md_file")
        [ "$fname" = "${foldername}.md" ] && continue
        [ "$fname" = "${foldername}_toc.md" ] && continue
        should_skip "$fname" "$ignore_str" && continue

        local fdesc
        fdesc="$(fm_field "$md_file" "description")"
        [ -z "$fdesc" ] && fdesc="(no description)"

        file_lines="${file_lines}"$'\n'"| [${fname}](${fname}) | ${fdesc} |"
    done

    # Tables
    local folder_table file_table
    if [ -n "$folder_lines" ]; then
        folder_table="| Folder | Description |"$'\n'"| ------ | ----------- |${folder_lines}"
    else
        folder_table="_No context subfolders found._"
    fi
    if [ -n "$file_lines" ]; then
        file_table="| File | Description |"$'\n'"| ---- | ----------- |${file_lines}"
    else
        file_table="_No context files found._"
    fi

    # Write
    {
        printf '%s\n' \
            "<!-- Auto-generated by build_toc.sh — edit ${foldername}.md instead -->" \
            "" \
            "# ${title}" \
            ""
        [ -n "$description" ] && printf '> %s\n\n' "$description"
        printf '%s\n\n%s\n\n' "## Subfolders" "$folder_table"
        printf '%s\n\n%s\n' "## Files" "$file_table"
    } > "$toc_file"
}

# ── Recursive walk ────────────────────────────────────────────────────────────

walk() {
    local dir="$1"
    local project_root="$2"
    local foldername=$(basename "$dir")
    local desc_file="$dir/${foldername}.md"

    [ -f "$desc_file" ] || return 0

    # Only write if real path is under project root
    local real_dir=$(cd "$dir" && pwd -P)
    case "$real_dir" in
        "$project_root"|"${project_root}"/*)
            local toc_file="$dir/${foldername}_toc.md"
            if ! $CHECK_MODE || needs_rebuild "$dir" "$toc_file"; then
                build_dir "$dir"
            fi
            ;;
        *)
            echo "  Skipping (outside project): $dir"
            ;;
    esac

    # Read walk-control config from this node
    local ignore_str=$(fenced_list_str "$desc_file" "config" "ignore")
    local follow_str=$(fenced_list_str "$desc_file" "config" "follow_symlinks")

    # Recurse into subdirectories
    for subdir in "$dir"/*/; do
        [ -d "$subdir" ] || continue
        local subname=$(basename "$subdir")
        should_skip "$subname" "$ignore_str" && continue

        # Symlinks: skip unless explicitly followed
        if [ -L "${subdir%/}" ]; then
            in_str_list "$subname" "$follow_str" || continue
        fi

        walk "$subdir" "$project_root"
    done
}

# ── Main ──────────────────────────────────────────────────────────────────────

main() {
    while [ $# -gt 0 ]; do
        case "$1" in
            --check) CHECK_MODE=true; shift ;;
            *) break ;;
        esac
    done

    local project_root
    project_root=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
    project_root=$(cd "$project_root" && pwd -P)

    echo "context-md: building TOC files..."

    if [ $# -eq 0 ]; then
        # Find root context nodes and walk from each.
        # A root node is a dir with <dirname>.md whose parent does NOT have <parentname>.md.
        find "$project_root" -name "*.md" \
             -not -name "*_toc.md" \
             -not -path "*/.git/*" \
             -not -path "*/node_modules/*" \
             | sort \
             | while IFS= read -r f; do
            local d=$(dirname "$f")
            local base=$(basename "$f" .md)
            local dname=$(basename "$d")
            [ "$base" = "$dname" ] || continue

            # Check parent is not a context node (making this a root)
            local parent=$(dirname "$d")
            local pname=$(basename "$parent")
            [ -f "$parent/${pname}.md" ] && continue

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
