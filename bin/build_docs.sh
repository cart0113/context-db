#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

BRUHA_ROOT="../GIT_BRUHA"

if [ ! -d "$BRUHA_ROOT/src/bruha" ]; then
    echo "Error: GIT_BRUHA not found at $BRUHA_ROOT" >&2
    echo "Clone it as a sibling: git clone ... ../GIT_BRUHA" >&2
    exit 1
fi

PYTHONPATH="$BRUHA_ROOT/src" python-main -c "
import bruha.docsify_ext_config as cfg
import bruha.sidebar_builder as sb
config = cfg.load_config('docs')
sb.write_sidebar('docs', config['top_level_folders_as_top_control'], config['content_folder'])
cfg.generate_config_js('docs')
print('Built _sidebar.md + bruha-config.js')
"

STAMP=$(date +%Y%m%d%H%M%S)
sed -i '' "s/?v=[0-9a-zA-Z]*/?v=${STAMP}/g" docs/index.html
echo "Cache bust: v=${STAMP}"

npx prettier --write "docs/src/**/*.md" "docs/themes/bruha-config.js" 2>&1 | tail -1
