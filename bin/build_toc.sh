#!/usr/bin/env bash
#
# build_toc.sh — Generate CONTEXT_TOC.md files from CONTEXT.yml config and
#                the front matter of context resources.
#
# For each CONTEXT/ directory that contains a CONTEXT.yml, this script:
#   1. Reads CONTEXT.yml for title, description, and indexing options
#   2. Reads CONTEXT_INSTRUCTIONS.md (if present) for LLM guidance prose
#   3. Scans for subfolders with their own CONTEXT.yml
#   4. Scans for sibling project dirs that have a CONTEXT/CONTEXT.yml
#   5. Scans for .md files in the CONTEXT/ directory
#   6. Writes a complete, fully-generated CONTEXT_TOC.md
#
# CONTEXT_TOC.md is never edited by hand.  Edit CONTEXT.yml and
# CONTEXT_INSTRUCTIONS.md instead.
#
# Usage:
#   bin/build_toc.sh                          Find and build all CONTEXT_TOC.md files
#   bin/build_toc.sh path/to/CONTEXT/         Build for a specific CONTEXT/ directory
#   bin/build_toc.sh path/to/CONTEXT.yml      Build for a specific CONTEXT.yml
#
# Requirements: bash 3.2+, awk (POSIX), mktemp — all standard on Unix/macOS/Linux.

set -eo pipefail

# ── YAML scalar helper ────────────────────────────────────────────────────────

# Read a scalar value from a simple YAML file.
# Usage: yml_val <file> <key> <default>
yml_val() {
    local val
    val=$(awk -v k="$2" '
        $0 ~ ("^" k ":") {
            sub("^" k ":[[:space:]]*", "")
            gsub(/^["'"'"']|["'"'"']$/, "")
            if ($0 != "" && $0 != "null" && $0 != "[]") print
            exit
        }
    ' "$1")
    echo "${val:-$3}"
}

# Print YAML list items to stdout, one per line.
# Supports inline  key: [a, b]  and block  key:\n  - a\n  - b  forms.
yml_list() {
    awk -v k="$2" '
        $0 ~ ("^" k ":[[:space:]]*\\[") {
            sub("^" k ":[[:space:]]*\\[", "")
            sub("\\].*$", "")
            n = split($0, parts, ",")
            for (i=1; i<=n; i++) {
                gsub(/^[[:space:]"'"'"']+|[[:space:]"'"'"']+$/, "", parts[i])
                if (parts[i] != "") print parts[i]
            }
            exit
        }
        $0 ~ ("^" k ":") { in_list=1; next }
        in_list && /^[[:space:]]+-/ {
            item=$0
            sub(/^[[:space:]]+-[[:space:]]*/, "", item)
            gsub(/^["'"'"']|["'"'"']$/, "", item)
            if (item != "") print item
        }
        in_list && /^[^[:space:]]/ { exit }
    ' "$1"
}

# Read a YAML list into a colon-separated string.
# Usage: var=$(yml_list_str <file> <key>)
yml_list_str() {
    yml_list "$1" "$2" | tr '\n' ':' | sed 's/:$//'
}

# ── Front-matter helper ───────────────────────────────────────────────────────

# Extract a field from a Markdown YAML front matter block (between --- lines).
# Usage: fm_field <file> <field>
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

# ── Skip logic ────────────────────────────────────────────────────────────────

# Return 0 (skip) or 1 (keep).
# ignore_str: colon-separated list of names to skip (no trailing slashes).
should_skip() {
    local name="$1" skip_us="$2" ignore_str="$3"
    local clean="${name%/}"
    [[ "$skip_us" == "true" && "$clean" == _* ]] && return 0
    if [ -n "$ignore_str" ]; then
        local item
        IFS=':' read -ra _items <<< "$ignore_str"
        for item in "${_items[@]}"; do
            item="${item%/}"
            [ "$clean" = "$item" ] && return 0
        done
    fi
    return 1
}

# Return 0 if name is in colon-separated list, 1 otherwise.
in_str_list() {
    local name="$1" list="$2"
    [ -z "$list" ] && return 1
    local item
    IFS=':' read -ra _items <<< "$list"
    for item in "${_items[@]}"; do
        item="${item%/}"
        [ "$name" = "$item" ] && return 0
    done
    return 1
}

# ── Core builder ──────────────────────────────────────────────────────────────

build_one() {
    local yml_file="$1"
    local context_dir project_dir
    context_dir="$(cd "$(dirname "$yml_file")" && pwd)"
    project_dir="$(dirname "$context_dir")"
    local toc_file="$context_dir/CONTEXT_TOC.md"

    # ── Read config ───────────────────────────────────────────────────────────

    local title description depth skip_us
    title=$(yml_val       "$yml_file" "title"           "(untitled)")
    description=$(yml_val "$yml_file" "description"     "")
    depth=$(yml_val       "$yml_file" "depth"           "1")
    skip_us=$(yml_val     "$yml_file" "skip_underscore" "true")

    local ignore_str read_only_str eager_read_str
    ignore_str=$(yml_list_str     "$yml_file" "ignore")
    read_only_str=$(yml_list_str  "$yml_file" "read_only")
    eager_read_str=$(yml_list_str "$yml_file" "eager_read")

    echo "  Building: $toc_file"

    # ── Gather folder entries ─────────────────────────────────────────────────

    local folder_lines=""

    # 1. Subfolders of CONTEXT/ that have their own CONTEXT.yml
    for subdir in "$context_dir"/*/; do
        [ -d "$subdir" ] || continue
        local dname
        dname="$(basename "$subdir")"
        should_skip "$dname" "$skip_us" "$ignore_str" && continue
        local sub_yml="$subdir/CONTEXT.yml"
        [ -f "$sub_yml" ] || continue

        local stitle sdesc ro_flag
        stitle="$(yml_val "$sub_yml" "title"       "$dname")"
        sdesc="$(yml_val  "$sub_yml" "description" "(no description)")"
        ro_flag=""
        in_str_list "$dname" "$read_only_str" && ro_flag=" *(read-only)*"

        folder_lines="${folder_lines}"$'\n'"| [${dname}/](${dname}/CONTEXT_TOC.md) | ${sdesc}${ro_flag} |"
    done

    # 2. Sibling project directories (adjacent to project root) with CONTEXT/CONTEXT.yml
    for sibling in "$project_dir"/*/; do
        [ -d "$sibling" ] || continue
        local sname
        sname="$(basename "$sibling")"
        [ "$sname" = "CONTEXT" ] && continue
        should_skip "$sname" "$skip_us" "$ignore_str" && continue
        local sib_yml="$sibling/CONTEXT/CONTEXT.yml"
        [ -f "$sib_yml" ] || continue

        local stitle sdesc ro_flag
        stitle="$(yml_val "$sib_yml" "title"       "$sname")"
        sdesc="$(yml_val  "$sib_yml" "description" "(no description)")"
        ro_flag=""
        in_str_list "$sname" "$read_only_str" && ro_flag=" *(read-only)*"

        folder_lines="${folder_lines}"$'\n'"| [../${sname}/CONTEXT/](../${sname}/CONTEXT/CONTEXT_TOC.md) | ${sdesc}${ro_flag} |"
    done

    # ── Gather file entries ───────────────────────────────────────────────────

    local file_lines=""

    for md_file in "$context_dir"/*.md; do
        [ -f "$md_file" ] || continue
        local fname
        fname="$(basename "$md_file")"
        case "$fname" in
            CONTEXT_TOC.md|CONTEXT_MD_SYSTEM_INSTRUCTIONS.md) continue ;;
        esac
        should_skip "$fname" "$skip_us" "$ignore_str" && continue

        local ftitle fdesc
        ftitle="$(fm_field "$md_file" "title")"
        fdesc="$(fm_field  "$md_file" "description")"
        [ -z "$ftitle" ] && ftitle="${fname%.md}"
        [ -z "$fdesc"  ] && fdesc="(no description)"

        file_lines="${file_lines}"$'\n'"| [${fname}](${fname}) | ${fdesc} |"
    done

    # ── Build table strings ───────────────────────────────────────────────────

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

    # ── Write the complete CONTEXT_TOC.md ────────────────────────────────────

    {
        printf '%s\n' \
            "<!-- AUTO-GENERATED by build_toc.sh — do not edit directly." \
            "     Edit CONTEXT.yml to change title, description, or indexing options. -->" \
            "" \
            "# ${title}" \
            ""
        if [ -n "$description" ]; then
            printf '> %s\n\n' "$description"
        fi
        if [ -n "$eager_read_str" ]; then
            printf '%s\n\n%s\n\n' \
                "## Always Load" \
                "*The following folders should be loaded whenever you read this TOC:*"
            IFS=':' read -ra _eager <<< "$eager_read_str"
            for item in "${_eager[@]}"; do
                item_clean="${item%/}"
                printf -- '- [%s/](%s/CONTEXT_TOC.md)\n' "$item_clean" "$item_clean"
            done
            echo ""
        fi
        printf '%s\n\n%s\n\n' "## Subfolders" "$folder_table"
        printf '%s\n\n%s\n' "## Files" "$file_table"
    } > "$toc_file"
}

# ── Main ──────────────────────────────────────────────────────────────────────

main() {
    echo "context-md: building TOC files..."

    if [ $# -eq 0 ]; then
        # Pass 1: collect all read_only targets into a temp file so we can skip them.
        local skip_file
        skip_file="$(mktemp)"

        while IFS= read -r -d '' yml; do
            local dir
            dir="$(cd "$(dirname "$yml")" && pwd)"
            yml_list "$yml" "read_only" | while IFS= read -r item; do
                [ -n "$item" ] && echo "${dir}/${item%/}/CONTEXT/CONTEXT.yml" >> "$skip_file"
            done
        done < <(find . -name "CONTEXT.yml" -not -path "*/.git/*" -print0)

        # Pass 2: build each CONTEXT.yml that is not in the skip list.
        while IFS= read -r -d '' yml; do
            local abs_yml
            abs_yml="$(cd "$(dirname "$yml")" && pwd)/CONTEXT.yml"
            if grep -qF "$abs_yml" "$skip_file" 2>/dev/null; then
                echo "  Skipping (read-only): $yml"
                continue
            fi
            build_one "$yml"
        done < <(find . -name "CONTEXT.yml" -not -path "*/.git/*" -print0)

        rm -f "$skip_file"

    elif [ -f "$1" ]; then
        case "$(basename "$1")" in
            CONTEXT.yml)    build_one "$1" ;;
            CONTEXT_TOC.md) build_one "$(dirname "$1")/CONTEXT.yml" ;;
            *) echo "Error: expected CONTEXT.yml or CONTEXT_TOC.md, got: $1" >&2; exit 1 ;;
        esac

    elif [ -d "$1" ]; then
        local yml="$1/CONTEXT.yml"
        [ -f "$yml" ] || { echo "Error: no CONTEXT.yml in $1" >&2; exit 1; }
        build_one "$yml"

    else
        echo "Error: '$1' is not a file or directory" >&2
        echo "Usage: build_toc.sh [CONTEXT.yml | CONTEXT_dir/ | (no args for all)]" >&2
        exit 1
    fi

    echo "Done."
}

main "$@"
