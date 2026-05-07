#!/usr/bin/env bash
set -euo pipefail

DOCS_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
EN_DIR="$DOCS_ROOT/docs/en"
POT_DIR="$DOCS_ROOT/docs/locales/templates"

mkdir -p "$POT_DIR"

echo "Extracting POT templates from $EN_DIR ..."
md2po -P "$EN_DIR/" "$POT_DIR/"

pot_count=$(find "$POT_DIR" -name "*.pot" | wc -l)
echo "Done. $pot_count POT files in $POT_DIR"