#!/usr/bin/env bash
#
# build_site.sh — Generate a Docsify site from a context-db directory.
#
# Uses show_toc.sh to generate TOC content dynamically — no static -toc.md
# files required.
#
# Usage:
#   bin/build_site.sh <source_dir> <output_dir>
#   bin/build_site.sh --embed <source_dir> <output_dir>
#   bin/build_site.sh --template file.html <source_dir> <output_dir>
#
# Flags:
#   --embed       Skip index.html / .nojekyll (for nesting under existing Docsify)
#   --template    Use a custom index.html instead of the default
#
# Requirements: bash 3.2+, awk

set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

EMBED=false
TEMPLATE=""

# ── Parsing ──────────────────���────────────────────��───────────────────────────

strip_frontmatter() {
    awk '
        BEGIN { in_fm=0; done_fm=0 }
        !done_fm && /^---$/ { in_fm++; if (in_fm >= 2) { done_fm=1 }; next }
        done_fm || in_fm == 0 { print }
    ' "$1"
}

read_desc() {
    awk '
        /^---$/ { fc++; next }
        fc == 1 && found && /^[[:space:]]/ {
            sub(/^[[:space:]]+/, "")
            if (val != "") val = val " "
            val = val $0
            next
        }
        fc == 1 && found { gsub(/^["'"'"']|["'"'"']$/, "", val); print val; exit }
        fc == 1 && /^description:/ {
            sub(/^description:[[:space:]]*/, "")
            if ($0 != "") { gsub(/^["'"'"']|["'"'"']$/, ""); print; exit }
            found = 1; val = ""
        }
        fc >= 2 { if (found) { gsub(/^["'"'"']|["'"'"']$/, "", val); print val }; exit }
    ' "$1"
}

find_desc_file() {
    local dir="$1" name
    name=$(basename "$(cd "$dir" && pwd -P)")
    [ -f "$dir/${name}.md" ] && { echo "$dir/${name}.md"; return 0; }
    [ -f "$dir/${name}-instructions.md" ] && { echo "$dir/${name}-instructions.md"; return 0; }
    local f
    for f in CONTEXT.md SKILL.md AGENT.md AGENTS.md; do
        [ -f "$dir/$f" ] && { echo "$dir/$f"; return 0; }
    done
    return 1
}

gen_toc() {
    "${SCRIPT_DIR}/show_toc.sh" "$1"
}

# ── Sidebar generation ────────────────────────────────────────────────────────

build_sidebar() {
    local src_dir="$1"
    local src_base="$2"
    local prefix="$3"
    local indent="$4"

    local pad=""
    for ((i=0; i<indent; i++)); do pad="  ${pad}"; done

    local toc_content
    toc_content=$(gen_toc "$src_dir")

    local desc="" path=""
    while IFS= read -r line || [ -n "$line" ]; do
        [[ -z "$line" ]] && continue
        [[ "$line" == "## "* ]] && continue

        if [[ "$line" == "- description: "* ]]; then
            desc="${line#- description: }"
        elif [[ "$line" == "  path: "* ]]; then
            path="${line#  path: }"
            if [[ "$path" == *-toc.md ]]; then
                local folder="${path%/*}"
                echo "${pad}- [${desc}](${prefix}${folder}/)"
                local sub_dir="${src_base}/${prefix}${folder}"
                if [ -d "$sub_dir" ]; then
                    build_sidebar "$sub_dir" "$src_base" "${prefix}${folder}/" $((indent+1))
                fi
            else
                echo "${pad}- [${desc}](${prefix}${path})"
            fi
            desc=""
            path=""
        fi
    done <<< "$toc_content"
}

# ── Content copy ───────────��───────────────────────────���──────────────────────

build_readme() {
    local src_dir="$1"
    local title="$2"

    local toc_content
    toc_content=$(gen_toc "$src_dir")

    echo "# ${title}"
    echo ""

    local desc="" path=""
    while IFS= read -r line || [ -n "$line" ]; do
        [[ -z "$line" ]] && continue
        [[ "$line" == "## "* ]] && continue

        if [[ "$line" == "- description: "* ]]; then
            desc="${line#- description: }"
        elif [[ "$line" == "  path: "* ]]; then
            path="${line#  path: }"
            if [[ "$path" == *-toc.md ]]; then
                local folder="${path%/*}"
                echo "- **[${desc}](${folder}/)**"
            else
                echo "- [${desc}](${path})"
            fi
            desc=""
            path=""
        fi
    done <<< "$toc_content"
}

copy_content() {
    local src_dir="$1"
    local src_base="$2"
    local out_base="$3"
    local prefix="$4"

    local toc_content
    toc_content=$(gen_toc "$src_dir")

    local path=""
    while IFS= read -r line || [ -n "$line" ]; do
        [[ "$line" != "  path: "* ]] && continue
        path="${line#  path: }"

        if [[ "$path" == *-toc.md ]]; then
            local folder="${path%/*}"
            local folder_src="${src_base}/${prefix}${folder}"
            local folder_out="${out_base}/${prefix}${folder}"
            mkdir -p "$folder_out"

            local sub_desc=""
            local sub_desc_file
            sub_desc_file=$(find_desc_file "$folder_src" 2>/dev/null) && \
                sub_desc=$(read_desc "$sub_desc_file")
            [ -z "$sub_desc" ] && sub_desc="$folder"
            build_readme "$folder_src" "$sub_desc" > "${folder_out}/README.md"
            copy_content "$folder_src" "$src_base" "$out_base" "${prefix}${folder}/"
        else
            local src_file="${src_base}/${prefix}${path}"
            local out_file="${out_base}/${prefix}${path}"
            if [ -f "$src_file" ]; then
                mkdir -p "$(dirname "$out_file")"
                strip_frontmatter "$src_file" > "$out_file"
            fi
        fi
        path=""
    done <<< "$toc_content"
}

# ── Main ──────────��──────────────────────────���──────────────────────────────��─

main() {
    while [ $# -gt 0 ]; do
        case "$1" in
            --embed)    EMBED=true; shift ;;
            --template) TEMPLATE="$2"; shift 2 ;;
            *) break ;;
        esac
    done

    if [ $# -lt 2 ]; then
        echo "Usage: bin/build_site.sh [--embed] [--template file.html] <source_dir> <output_dir>" >&2
        exit 1
    fi

    local src_dir="${1%/}"
    local out_dir="${2%/}"

    # Verify source is a context-db folder
    find_desc_file "$src_dir" >/dev/null 2>&1 || {
        echo "Error: '$src_dir' is not a context-db folder (no description file found)" >&2
        exit 1
    }

    # Root description
    local desc_file root_desc=""
    desc_file=$(find_desc_file "$src_dir" 2>/dev/null) && \
        root_desc=$(read_desc "$desc_file")
    local foldername
    foldername=$(basename "$(cd "$src_dir" && pwd)")
    [ -z "$root_desc" ] && root_desc="$foldername"

    echo "context-db: building site from $src_dir → $out_dir"

    mkdir -p "$out_dir"

    # Sidebar
    {
        $EMBED && echo "- [← Back](/)"
        echo "- **${root_desc}**"
        build_sidebar "$src_dir" "$src_dir" "" 1
    } > "${out_dir}/_sidebar.md"
    echo "  Built: _sidebar.md"

    # Root README
    build_readme "$src_dir" "$root_desc" > "${out_dir}/README.md"
    echo "  Built: README.md"

    # Content files (frontmatter stripped)
    copy_content "$src_dir" "$src_dir" "$out_dir" ""
    echo "  Copied content files"

    # index.html and .nojekyll (standalone only)
    if ! $EMBED; then
        if [ -n "$TEMPLATE" ] && [ -f "$TEMPLATE" ]; then
            cp "$TEMPLATE" "${out_dir}/index.html"
        elif [ -f "${PROJECT_ROOT}/templates/docsify-index.html" ]; then
            cp "${PROJECT_ROOT}/templates/docsify-index.html" "${out_dir}/index.html"
        else
            generate_default_index > "${out_dir}/index.html"
        fi
        touch "${out_dir}/.nojekyll"
        echo "  Built: index.html"
    fi

    echo "Done."
}

generate_default_index() {
    cat <<'HTML'
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>context-db</title>
  <link rel="stylesheet" href="//cdn.jsdelivr.net/npm/docsify@4/lib/themes/buble.css">
  <style>
    :root { --theme-color: #2b6cb0; }
    .sidebar-nav li > a { font-size: 0.92em; }
    .markdown-section pre > code { font-size: 0.88em; }
  </style>
</head>
<body>
  <div id="app"></div>
  <script>
    window.$docsify = {
      loadSidebar: true,
      subMaxLevel: 2,
      auto2top: true,
      search: {
        placeholder: 'Search',
        noData: 'No results.',
        depth: 3,
      },
    }
  </script>
  <script src="//cdn.jsdelivr.net/npm/docsify@4"></script>
  <script src="//cdn.jsdelivr.net/npm/docsify/lib/plugins/search.min.js"></script>
</body>
</html>
HTML
}

main "$@"
