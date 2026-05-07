#!/usr/bin/env bash
set -euo pipefail

DOCS_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
EN_DIR="$DOCS_ROOT/docs/en"
PO_DIR="$DOCS_ROOT/docs/locales/nl/LC_MESSAGES"
NL_DIR="$DOCS_ROOT/docs/nl"
FIX_SCRIPT="$DOCS_ROOT/scripts/i18n/fix_admonitions.py"

if [ ! -d "$PO_DIR" ]; then
    echo "Error: PO directory not found at $PO_DIR"
    echo "Run extract-pot.sh and update-po.sh first."
    exit 1
fi

# Clean and regenerate
rm -rf "$NL_DIR"
mkdir -p "$NL_DIR"

echo "Generating Dutch markdown from PO files ..."
po2md -t "$EN_DIR/" -i "$PO_DIR/" -o "$NL_DIR/"

# Fix MkDocs admonition formatting (po2md collapses them)
echo "Fixing admonition formatting ..."
python3 "$FIX_SCRIPT" "$NL_DIR"

nl_count=$(find "$NL_DIR" -name "*.md" | wc -l)
echo "Done. $nl_count Dutch markdown files in $NL_DIR"