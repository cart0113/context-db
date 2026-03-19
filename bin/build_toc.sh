#!/usr/bin/env bash
#
# build_toc.sh — Generate <folder>_toc.md files from <folder>.md configs and
#                front matter of context resources.
#
# For each context directory that contains a <folder>.md, this script:
#   1. Reads the ```yaml description``` and optional ```yaml config``` blocks
#   2. Scans for subfolders with their own <subfolder>.md
#   3. Scans for .md context documents
#   4. Writes a fully-generated <folder>_toc.md
#
# The _toc.md files are never edited by hand. Edit <folder>.md instead.
#
# Usage:
#   bin/build_toc.sh                   Find and build all _toc.md files
#   bin/build_toc.sh CONTEXT/          Build one specific directory
#   bin/build_toc.sh --check           Only rebuild if source files changed
#
# Requirements: bash 3.2+, awk (POSIX), mktemp

set -eo pipefail

# ── Fenced YAML parsing ──────────────────────────────────────────────────────

# Extract a scalar value from a fenced YAML block: ```yaml <blockname> ... ```
# Usage: fenced_val <file> <blockname> <key> <default>
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

# Print list items from a fenced YAML block, one per line.
# Handles inline [a, b] and block - item forms.
fenced_list() {
    awk -v block="$2" -v k="$3" '
        $0 ~ ("^```yaml " block) { in_b=1; next }
        in_b && /^```/ { exit }
        in_b && $0 ~ ("^" k ":[[:space:]]*\\[") {
            sub("^" k ":[[:space:]]*\\[", "")
            sub("\\].*$", "")
            n = split($0, parts, ",")
            for (i=1; i<=n; i++) {
                gsub(/^[[:space:]]+|[[:space:]]+$/, "", parts[i])
                if (parts[i] != "") print parts[i]
            }
            exit
        }
        in_b && $0 ~ ("^" k ":") { in_list=1; next }
        in_b && in_list && /^[[:space:]]+-/ {
            item=$0
            sub(/^[[:space:]]+-[[:space:]]*/, "", item)
            gsub(/^["'"'"']|["'"'"']$/, "", item)
            if (item != "") print item
        }
        in_b && in_list && /^[^[:space:]]/ { exit }
    ' "$1"
}

# Colon-separated list string from a fenced YAML block.
fenced_list_str() {
    fenced_list "$1" "$2" "$3" | tr '\n' ':' | sed 's/:$//'
}

# ── Front-matter parsing ─────────────────────────────────────────────────────

# Extract a field from standard YAML front matter (--- block).
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

should_skip() {
    local name="$1" skip_us="$2" ignore_str="$3"
    local clean="${name%/}"
    [ "$skip_us" = "true" ] && case "$clean" in _*) return 0 ;; esac
    if [ -n "$ignore_str" ]; then
        IFS=':' read -ra _items <<< "$ignore_str"
        for item in "${_items[@]}"; do
            item="${item%/}"
            [ "$clean" = "$item" ] && return 0
        done
    fi
    return 1
}

in_str_list() {
    local name="$1" list="$2"
    [ -z "$list" ] && return 1
    IFS=':' read -ra _items <<< "$list"
    for item in "${_items[@]}"; do
        item="${item%/}"
        [ "$name" = "$item" ] && return 0
    done
    return 1
}

# ── Change detection ──────────────────────────────────────────────────────────

# Return 0 if sources are newer than the toc file, 1 if toc is up to date.
needs_rebuild() {
    local dir="$1" toc_file="$2"
    [ ! -f "$toc_file" ] && return 0

    local toc_mtime
    toc_mtime=$(stat -f %m "$toc_file" 2>/dev/null || stat -c %Y "$toc_file" 2>/dev/null)

    # Check <folder>.md
    local foldername
    foldername="$(basename "$dir")"
    local desc_file="$dir/${foldername}.md"
    if [ -f "$desc_file" ]; then
        local m
        m=$(stat -f %m "$desc_file" 2>/dev/null || stat -c %Y "$desc_file" 2>/dev/null)
        [ "$m" -gt "$toc_mtime" ] && return 0
    fi

    # Check all .md files in this directory
    for f in "$dir"/*.md; do
        [ -f "$f" ] || continue
        local m
        m=$(stat -f %m "$f" 2>/dev/null || stat -c %Y "$f" 2>/dev/null)
        [ "$m" -gt "$toc_mtime" ] && return 0
    done

    # Check subfolder <name>.md files (one level)
    for subdir in "$dir"/*/; do
        [ -d "$subdir" ] || continue
        [ -L "$subdir" ] && continue  # skip symlinks for change detection
        local subname
        subname="$(basename "$subdir")"
        local sub_desc="$subdir/${subname}.md"
        if [ -f "$sub_desc" ]; then
            local m
            m=$(stat -f %m "$sub_desc" 2>/dev/null || stat -c %Y "$sub_desc" 2>/dev/null)
            [ "$m" -gt "$toc_mtime" ] && return 0
        fi
    done

    return 1
}

# ── Core builder ──────────────────────────────────────────────────────────────

build_dir() {
    local dir="$1"
    local foldername
    foldername="$(basename "$dir")"
    local desc_file="$dir/${foldername}.md"
    local toc_file="$dir/${foldername}_toc.md"

    [ -f "$desc_file" ] || return 0

    # ── Read description block ────────────────────────────────────────────────

    local title description
    title=$(fenced_val       "$desc_file" "description" "title"       "(untitled)")
    description=$(fenced_val "$desc_file" "description" "description" "")

    # ── Read config block (optional) ──────────────────────────────────────────

    local skip_us ignore_str read_only_str eager_read_str
    skip_us=$(fenced_val        "$desc_file" "config" "skip_underscore" "true")
    ignore_str=$(fenced_list_str   "$desc_file" "config" "ignore")
    read_only_str=$(fenced_list_str "$desc_file" "config" "read_only")
    eager_read_str=$(fenced_list_str "$desc_file" "config" "eager_read")

    echo "  Building: $toc_file"

    # ── Gather folder entries ─────────────────────────────────────────────────

    local folder_lines=""

    for subdir in "$dir"/*/; do
        [ -d "$subdir" ] || continue
        local subname
        subname="$(basename "$subdir")"
        should_skip "$subname" "$skip_us" "$ignore_str" && continue
        local sub_desc="$subdir/${subname}.md"
        [ -f "$sub_desc" ] || continue

        local stitle sdesc ro_flag
        # For symlinks, read the <folder>.md from within — but use fenced_val
        stitle="$(fenced_val "$sub_desc" "description" "title"       "$subname")"
        sdesc="$(fenced_val  "$sub_desc" "description" "description" "(no description)")"
        ro_flag=""
        if [ -L "$subdir" ] || in_str_list "$subname" "$read_only_str"; then
            ro_flag=" *(read-only)*"
        fi

        folder_lines="${folder_lines}"$'\n'"| [${subname}/](${subname}/${subname}_toc.md) | ${sdesc}${ro_flag} |"
    done

    # ── Gather file entries ───────────────────────────────────────────────────

    local file_lines=""

    for md_file in "$dir"/*.md; do
        [ -f "$md_file" ] || continue
        local fname
        fname="$(basename "$md_file")"
        [ "$fname" = "${foldername}.md" ] && continue
        [ "$fname" = "${foldername}_toc.md" ] && continue
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

    # ── Write the TOC ────────────────────────────────────────────────────────

    {
        printf '%s\n' \
            "<!-- Auto-generated by build_toc.sh — edit ${foldername}.md instead -->" \
            "" \
            "# ${title}" \
            ""
        if [ -n "$description" ]; then
            printf '> %s\n\n' "$description"
        fi
        if [ -n "$eager_read_str" ]; then
            printf '%s\n\n%s\n\n' \
                "## Always Load" \
                "*Load these folders whenever you read this TOC:*"
            IFS=':' read -ra _eager <<< "$eager_read_str"
            for item in "${_eager[@]}"; do
                item="${item%/}"
                printf -- '- [%s/](%s/%s_toc.md)\n' "$item" "$item" "$item"
            done
            echo ""
        fi
        printf '%s\n\n%s\n\n' "## Subfolders" "$folder_table"
        printf '%s\n\n%s\n' "## Files" "$file_table"
    } > "$toc_file"
}

# ── Main ──────────────────────────────────────────────────────────────────────

CHECK_MODE=false

main() {
    # Parse flags
    while [ $# -gt 0 ]; do
        case "$1" in
            --check) CHECK_MODE=true; shift ;;
            *) break ;;
        esac
    done

    echo "context-md: building TOC files..."

    if [ $# -eq 0 ]; then
        # Collect read_only targets so we skip rebuilding symlinked dirs
        local skip_file
        skip_file="$(mktemp)"

        # Find all context dirs: directories containing <dirname>.md
        while IFS= read -r -d '' dir; do
            local dname
            dname="$(basename "$dir")"
            local desc="$dir/${dname}.md"
            [ -f "$desc" ] || continue

            # Skip symlinked directories (never rebuild across symlinks)
            [ -L "$dir" ] && continue

            local toc="$dir/${dname}_toc.md"

            if $CHECK_MODE && ! needs_rebuild "$dir" "$toc"; then
                continue
            fi

            build_dir "$dir"
        done < <(find . -name "*.md" -not -path "*/.git/*" -print0 \
                 | xargs -0 -I{} dirname {} \
                 | sort -u \
                 | while IFS= read -r d; do
                     dname="$(basename "$d")"
                     [ -f "$d/${dname}.md" ] && printf '%s\0' "$d"
                   done)

        rm -f "$skip_file"

    elif [ -d "$1" ]; then
        local dir
        dir="$(cd "$1" && pwd)"
        build_dir "$dir"

    elif [ -f "$1" ]; then
        local dir
        dir="$(cd "$(dirname "$1")" && pwd)"
        build_dir "$dir"

    else
        echo "Error: '$1' is not a file or directory" >&2
        echo "Usage: build_toc.sh [--check] [directory | file]" >&2
        exit 1
    fi

    echo "Done."
}

main "$@"
