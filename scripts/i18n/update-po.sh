#!/usr/bin/env bash
set -euo pipefail

DOCS_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
POT_DIR="$DOCS_ROOT/docs/locales/templates"
PO_DIR="$DOCS_ROOT/docs/locales/nl/LC_MESSAGES"

mkdir -p "$PO_DIR"

echo "Merging POT updates into NL PO files ..."

for pot_file in "$POT_DIR"/*.pot; do
    name=$(basename "$pot_file" .pot)
    pot2po "$pot_file" "$PO_DIR/${name}.po"
    echo "  $name: done"
done

po_count=$(find "$PO_DIR" -name "*.po" | wc -l)
echo "Done. $po_count PO files in $PO_DIR"