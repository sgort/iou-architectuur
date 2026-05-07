#!/usr/bin/env bash
set -euo pipefail

DOCS_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
EN_DIR="$DOCS_ROOT/docs/en"
PO_DIR="$DOCS_ROOT/docs/locales/nl/LC_MESSAGES"
NL_DIR="$DOCS_ROOT/docs/nl"
FIX_SCRIPT="$DOCS_ROOT/scripts/i18n/fix_admonitions.py"

COMPONENTS="ronl-business-api cpsv-editor linked-data-explorer cprmv-api contributing"

if [ ! -d "$PO_DIR" ]; then
    echo "Error: PO directory not found at $PO_DIR"
    echo "Run extract-pot.sh and update-po.sh first."
    exit 1
fi

# Clean and regenerate
rm -rf "$NL_DIR"
mkdir -p "$NL_DIR"

echo "Generating Dutch markdown from PO files ..."

for comp in $COMPONENTS; do
    po_file="$PO_DIR/${comp}.po"
    if [ -f "$po_file" ] && [ -d "$EN_DIR/$comp" ]; then
        mkdir -p "$NL_DIR/$comp"
        po2md -t "$EN_DIR/$comp" -i "$po_file" -o "$NL_DIR/$comp"
        echo "  $comp: done"
    fi
done

# index.md
if [ -f "$PO_DIR/index.po" ] && [ -f "$EN_DIR/index.md" ]; then
    po2md -t "$EN_DIR/index.md" -i "$PO_DIR/index.po" -o "$NL_DIR/index.md"
    echo "  index: done"
fi

# Fix MkDocs admonition formatting (po2md collapses them)
echo "Fixing admonition formatting ..."
python "$FIX_SCRIPT" "$NL_DIR"

nl_count=$(find "$NL_DIR" -name "*.md" | wc -l)
echo "Done. $nl_count Dutch markdown files in $NL_DIR"