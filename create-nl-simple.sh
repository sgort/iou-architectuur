#!/bin/bash

# Super simple - just create each file one by one

echo "Creating Dutch placeholder files..."
echo ""

# Function to create a simple placeholder
mkfile() {
    mkdir -p "$(dirname "$1")"
    echo "# $2" > "$1"
    echo "" >> "$1"
    echo "**Documentatie in ontwikkeling**" >> "$1"
    echo "" >> "$1"
    echo "---" >> "$1"
    echo "" >> "$1"
    echo "**Pad**: \`$1\`" >> "$1"
    echo "**Status**: Concept" >> "$1"
    echo "  ✓ $1"
}

# Check if file exists and is small (placeholder)
check() {
    if [ -f "$1" ]; then
        size=$(wc -c < "$1")
        if [ $size -gt 300 ]; then
            echo "  ⊙ $1 (has content, skipped)"
            return 1
        fi
    fi
    return 0
}

# IOU Architectuur
check "docs/nl/iou-architectuur/index.md" && mkfile "docs/nl/iou-architectuur/index.md" "IOU Architectuur Framework"
check "docs/nl/iou-architectuur/ontologische-architectuur.md" && mkfile "docs/nl/iou-architectuur/ontologische-architectuur.md" "Ontologische Architectuur"
check "docs/nl/iou-architectuur/implementatie-architectuur.md" && mkfile "docs/nl/iou-architectuur/implementatie-architectuur.md" "Implementatie Architectuur"
check "docs/nl/iou-architectuur/roadmap-evaluatie.md" && mkfile "docs/nl/iou-architectuur/roadmap-evaluatie.md" "Roadmap & Evaluatie"

echo ""

# CPSV Editor
check "docs/nl/cpsv-editor/index.md" && mkfile "docs/nl/cpsv-editor/index.md" "CPSV Editor"
check "docs/nl/cpsv-editor/features.md" && mkfile "docs/nl/cpsv-editor/features.md" "Functionaliteit"
check "docs/nl/cpsv-editor/user-guide/getting-started.md" && mkfile "docs/nl/cpsv-editor/user-guide/getting-started.md" "Aan de Slag"
check "docs/nl/cpsv-editor/user-guide/service-definition.md" && mkfile "docs/nl/cpsv-editor/user-guide/service-definition.md" "Dienst Definitie"
check "docs/nl/cpsv-editor/user-guide/rules-parameters.md" && mkfile "docs/nl/cpsv-editor/user-guide/rules-parameters.md" "Regels & Parameters"
check "docs/nl/cpsv-editor/user-guide/dmn-integration.md" && mkfile "docs/nl/cpsv-editor/user-guide/dmn-integration.md" "DMN Integratie"
check "docs/nl/cpsv-editor/user-guide/import-export.md" && mkfile "docs/nl/cpsv-editor/user-guide/import-export.md" "Importeren & Exporteren"
check "docs/nl/cpsv-editor/technical/architecture.md" && mkfile "docs/nl/cpsv-editor/technical/architecture.md" "Architectuur"
check "docs/nl/cpsv-editor/technical/standards-compliance.md" && mkfile "docs/nl/cpsv-editor/technical/standards-compliance.md" "Standaarden Naleving"
check "docs/nl/cpsv-editor/technical/field-mapping.md" && mkfile "docs/nl/cpsv-editor/technical/field-mapping.md" "Veld Mapping"
check "docs/nl/cpsv-editor/technical/development.md" && mkfile "docs/nl/cpsv-editor/technical/development.md" "Ontwikkeling"

echo ""

# Linked Data Explorer
check "docs/nl/linked-data-explorer/index.md" && mkfile "docs/nl/linked-data-explorer/index.md" "Linked Data Explorer"
check "docs/nl/linked-data-explorer/features.md" && mkfile "docs/nl/linked-data-explorer/features.md" "Functionaliteit"
check "docs/nl/linked-data-explorer/user-guide/getting-started.md" && mkfile "docs/nl/linked-data-explorer/user-guide/getting-started.md" "Aan de Slag"
check "docs/nl/linked-data-explorer/user-guide/sparql-queries.md" && mkfile "docs/nl/linked-data-explorer/user-guide/sparql-queries.md" "SPARQL Queries"
check "docs/nl/linked-data-explorer/user-guide/dmn-orchestration.md" && mkfile "docs/nl/linked-data-explorer/user-guide/dmn-orchestration.md" "DMN Orkestratie"
check "docs/nl/linked-data-explorer/user-guide/chain-building.md" && mkfile "docs/nl/linked-data-explorer/user-guide/chain-building.md" "Keten Opbouw"
check "docs/nl/linked-data-explorer/technical/architecture.md" && mkfile "docs/nl/linked-data-explorer/technical/architecture.md" "Architectuur"
check "docs/nl/linked-data-explorer/technical/api-reference.md" && mkfile "docs/nl/linked-data-explorer/technical/api-reference.md" "API Referentie"
check "docs/nl/linked-data-explorer/technical/development.md" && mkfile "docs/nl/linked-data-explorer/technical/development.md" "Ontwikkeling"

echo ""

# Gedeelde Backend
check "docs/nl/gedeelde-backend/index.md" && mkfile "docs/nl/gedeelde-backend/index.md" "Gedeelde Backend"
check "docs/nl/gedeelde-backend/api-documentatie.md" && mkfile "docs/nl/gedeelde-backend/api-documentatie.md" "API Documentatie"
check "docs/nl/gedeelde-backend/triplydb-integratie.md" && mkfile "docs/nl/gedeelde-backend/triplydb-integratie.md" "TriplyDB Integratie"
check "docs/nl/gedeelde-backend/operaton-integratie.md" && mkfile "docs/nl/gedeelde-backend/operaton-integratie.md" "Operaton Integratie"
check "docs/nl/gedeelde-backend/deployment.md" && mkfile "docs/nl/gedeelde-backend/deployment.md" "Deployment"

echo ""

# Bijdragen
check "docs/nl/bijdragen/index.md" && mkfile "docs/nl/bijdragen/index.md" "Bijdragen"
check "docs/nl/bijdragen/documentatie-gids.md" && mkfile "docs/nl/bijdragen/documentatie-gids.md" "Documentatie Gids"
check "docs/nl/bijdragen/code-standaarden.md" && mkfile "docs/nl/bijdragen/code-standaarden.md" "Code Standaarden"

echo ""
echo "✅ Done! Run: ./verify-structure.sh"
