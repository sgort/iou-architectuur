#!/usr/bin/env bash
set -euo pipefail

DOCS_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
POT_DIR="$DOCS_ROOT/docs/locales/templates"
PO_DIR="$DOCS_ROOT/docs/locales/nl/LC_MESSAGES"

mkdir -p "$PO_DIR"

echo "Merging POT updates into NL PO files ..."
pot2po "$POT_DIR/" "$PO_DIR/"

po_count=$(find "$PO_DIR" -name "*.po" | wc -l)
echo "Done. $po_count PO files in $PO_DIR"