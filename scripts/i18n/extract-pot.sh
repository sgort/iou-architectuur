#!/usr/bin/env bash
set -euo pipefail

DOCS_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
EN_DIR="$DOCS_ROOT/docs/en"
POT_DIR="$DOCS_ROOT/docs/locales/templates"

mkdir -p "$POT_DIR"

COMPONENTS="ronl-business-api cpsv-editor linked-data-explorer cprmv-api contributing"

echo "Extracting POT templates from $EN_DIR ..."

for comp in $COMPONENTS; do
    if [ -d "$EN_DIR/$comp" ]; then
        md2po -P --multifile=onefile "$EN_DIR/$comp" "$POT_DIR/${comp}.pot"
        echo "  $comp: done"
    fi
done

# index.md lives at the root
if [ -f "$EN_DIR/index.md" ]; then
    md2po -P "$EN_DIR/index.md" "$POT_DIR/index.pot"
    echo "  index: done"
fi

pot_count=$(find "$POT_DIR" -name "*.pot" | wc -l)
echo "Done. $pot_count POT files in $POT_DIR"