#!/bin/bash
set -e

echo "📚 Creating ALL placeholder files"
echo "================================="
echo ""

count=0

create() {
    local file=$1
    local title=$2
    local lang=$3
    
    if [ -f "$file" ]; then
        size=$(wc -c < "$file")
        if [ $size -gt 300 ]; then
            return  # Skip files with content
        fi
    fi
    
    mkdir -p "$(dirname "$file")"
    
    if [ "$lang" = "nl" ]; then
        cat > "$file" << EOF
# ${title}

**Documentatie in ontwikkeling**

---

**Pad**: \`${file}\`  
**Status**: Concept
EOF
    else
        cat > "$file" << EOF
# ${title}

**Documentation in progress**

---

**Path**: \`${file}\`  
**Status**: Draft
EOF
    fi
    
    echo "  ✓ $file"
    ((count++))
}

echo "English files..."
create "docs/en/index.md" "IOU Architecture Documentation" "en"
create "docs/en/iou-architecture/index.md" "IOU Architecture Framework" "en"
create "docs/en/iou-architecture/ontological-architecture.md" "Ontological Architecture" "en"
create "docs/en/iou-architecture/implementation-architecture.md" "Implementation Architecture" "en"
create "docs/en/iou-architecture/roadmap-evaluation.md" "Roadmap & Evaluation" "en"
create "docs/en/cpsv-editor/index.md" "CPSV Editor" "en"
create "docs/en/cpsv-editor/features.md" "Features" "en"
create "docs/en/cpsv-editor/user-guide/getting-started.md" "Getting Started" "en"
create "docs/en/cpsv-editor/user-guide/service-definition.md" "Service Definition" "en"
create "docs/en/cpsv-editor/user-guide/rules-parameters.md" "Rules & Parameters" "en"
create "docs/en/cpsv-editor/user-guide/dmn-integration.md" "DMN Integration" "en"
create "docs/en/cpsv-editor/user-guide/import-export.md" "Import & Export" "en"
create "docs/en/cpsv-editor/technical/architecture.md" "Architecture" "en"
create "docs/en/cpsv-editor/technical/standards-compliance.md" "Standards Compliance" "en"
create "docs/en/cpsv-editor/technical/field-mapping.md" "Field Mapping" "en"
create "docs/en/cpsv-editor/technical/development.md" "Development" "en"
create "docs/en/linked-data-explorer/index.md" "Linked Data Explorer" "en"
create "docs/en/linked-data-explorer/features.md" "Features" "en"
create "docs/en/linked-data-explorer/user-guide/getting-started.md" "Getting Started" "en"
create "docs/en/linked-data-explorer/user-guide/sparql-queries.md" "SPARQL Queries" "en"
create "docs/en/linked-data-explorer/user-guide/dmn-orchestration.md" "DMN Orchestration" "en"
create "docs/en/linked-data-explorer/user-guide/chain-building.md" "Chain Building" "en"
create "docs/en/linked-data-explorer/technical/architecture.md" "Architecture" "en"
create "docs/en/linked-data-explorer/technical/api-reference.md" "API Reference" "en"
create "docs/en/linked-data-explorer/technical/development.md" "Development" "en"
create "docs/en/shared-backend/index.md" "Shared Backend" "en"
create "docs/en/shared-backend/api-documentation.md" "API Documentation" "en"
create "docs/en/shared-backend/triplydb-integration.md" "TriplyDB Integration" "en"
create "docs/en/shared-backend/operaton-integration.md" "Operaton Integration" "en"
create "docs/en/shared-backend/deployment.md" "Deployment" "en"
create "docs/en/contributing/index.md" "Contributing" "en"
create "docs/en/contributing/documentation-guide.md" "Documentation Guide" "en"
create "docs/en/contributing/code-standards.md" "Code Standards" "en"

echo ""
echo "Dutch files..."
create "docs/nl/index.md" "IOU Architectuur Documentatie" "nl"
create "docs/nl/iou-architectuur/index.md" "IOU Architectuur Framework" "nl"
create "docs/nl/iou-architectuur/ontologische-architectuur.md" "Ontologische Architectuur" "nl"
create "docs/nl/iou-architectuur/implementatie-architectuur.md" "Implementatie Architectuur" "nl"
create "docs/nl/iou-architectuur/roadmap-evaluatie.md" "Roadmap & Evaluatie" "nl"
create "docs/nl/cpsv-editor/index.md" "CPSV Editor" "nl"
create "docs/nl/cpsv-editor/features.md" "Functionaliteit" "nl"
create "docs/nl/cpsv-editor/user-guide/getting-started.md" "Aan de Slag" "nl"
create "docs/nl/cpsv-editor/user-guide/service-definition.md" "Dienst Definitie" "nl"
create "docs/nl/cpsv-editor/user-guide/rules-parameters.md" "Regels & Parameters" "nl"
create "docs/nl/cpsv-editor/user-guide/dmn-integration.md" "DMN Integratie" "nl"
create "docs/nl/cpsv-editor/user-guide/import-export.md" "Importeren & Exporteren" "nl"
create "docs/nl/cpsv-editor/technical/architecture.md" "Architectuur" "nl"
create "docs/nl/cpsv-editor/technical/standards-compliance.md" "Standaarden Naleving" "nl"
create "docs/nl/cpsv-editor/technical/field-mapping.md" "Veld Mapping" "nl"
create "docs/nl/cpsv-editor/technical/development.md" "Ontwikkeling" "nl"
create "docs/nl/linked-data-explorer/index.md" "Linked Data Explorer" "nl"
create "docs/nl/linked-data-explorer/features.md" "Functionaliteit" "nl"
create "docs/nl/linked-data-explorer/user-guide/getting-started.md" "Aan de Slag" "nl"
create "docs/nl/linked-data-explorer/user-guide/sparql-queries.md" "SPARQL Queries" "nl"
create "docs/nl/linked-data-explorer/user-guide/dmn-orchestration.md" "DMN Orkestratie" "nl"
create "docs/nl/linked-data-explorer/user-guide/chain-building.md" "Keten Opbouw" "nl"
create "docs/nl/linked-data-explorer/technical/architecture.md" "Architectuur" "nl"
create "docs/nl/linked-data-explorer/technical/api-reference.md" "API Referentie" "nl"
create "docs/nl/linked-data-explorer/technical/development.md" "Ontwikkeling" "nl"
create "docs/nl/gedeelde-backend/index.md" "Gedeelde Backend" "nl"
create "docs/nl/gedeelde-backend/api-documentatie.md" "API Documentatie" "nl"
create "docs/nl/gedeelde-backend/triplydb-integratie.md" "TriplyDB Integratie" "nl"
create "docs/nl/gedeelde-backend/operaton-integratie.md" "Operaton Integratie" "nl"
create "docs/nl/gedeelde-backend/deployment.md" "Deployment" "nl"
create "docs/nl/bijdragen/index.md" "Bijdragen" "nl"
create "docs/nl/bijdragen/documentatie-gids.md" "Documentatie Gids" "nl"
create "docs/nl/bijdragen/code-standaarden.md" "Code Standaarden" "nl"

echo ""
echo "================================="
echo "✅ Created $count new files"
echo "================================="
echo ""
echo "Run: ./verify-structure.sh"