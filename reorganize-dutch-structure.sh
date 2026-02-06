#!/bin/bash

# Reorganize Dutch folder structure to match English
# This allows the i18n plugin to find files correctly

set -e

echo "🔄 Reorganizing Dutch folder structure"
echo "======================================"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Moving files to match English structure...${NC}"
echo ""

# iou-architectuur → iou-architecture
if [ -d "docs/nl/iou-architectuur" ]; then
    echo "  Moving iou-architectuur → iou-architecture"
    mv docs/nl/iou-architectuur docs/nl/iou-architecture
    echo -e "${GREEN}  ✓${NC} Done"
else
    echo "  ⊙ iou-architecture already correct"
fi

# gedeelde-backend → shared-backend
if [ -d "docs/nl/gedeelde-backend" ]; then
    echo "  Moving gedeelde-backend → shared-backend"
    mv docs/nl/gedeelde-backend docs/nl/shared-backend
    echo -e "${GREEN}  ✓${NC} Done"
else
    echo "  ⊙ shared-backend already correct"
fi

# bijdragen → contributing
if [ -d "docs/nl/bijdragen" ]; then
    echo "  Moving bijdragen → contributing"
    mv docs/nl/bijdragen docs/nl/contributing
    echo -e "${GREEN}  ✓${NC} Done"
else
    echo "  ⊙ contributing already correct"
fi

echo ""

# Rename Dutch filenames to match English
echo -e "${BLUE}Renaming files to match English structure...${NC}"
echo ""

# IOU Architecture files
if [ -f "docs/nl/iou-architecture/ontologische-architectuur.md" ]; then
    mv docs/nl/iou-architecture/ontologische-architectuur.md docs/nl/iou-architecture/ontological-architecture.md
    echo -e "${GREEN}  ✓${NC} ontologische-architectuur.md → ontological-architecture.md"
fi

if [ -f "docs/nl/iou-architecture/implementatie-architectuur.md" ]; then
    mv docs/nl/iou-architecture/implementatie-architectuur.md docs/nl/iou-architecture/implementation-architecture.md
    echo -e "${GREEN}  ✓${NC} implementatie-architectuur.md → implementation-architecture.md"
fi

if [ -f "docs/nl/iou-architecture/roadmap-evaluatie.md" ]; then
    mv docs/nl/iou-architecture/roadmap-evaluatie.md docs/nl/iou-architecture/roadmap-evaluation.md
    echo -e "${GREEN}  ✓${NC} roadmap-evaluatie.md → roadmap-evaluation.md"
fi

# Shared Backend files
if [ -f "docs/nl/shared-backend/api-documentatie.md" ]; then
    mv docs/nl/shared-backend/api-documentatie.md docs/nl/shared-backend/api-documentation.md
    echo -e "${GREEN}  ✓${NC} api-documentatie.md → api-documentation.md"
fi

if [ -f "docs/nl/shared-backend/triplydb-integratie.md" ]; then
    mv docs/nl/shared-backend/triplydb-integratie.md docs/nl/shared-backend/triplydb-integration.md
    echo -e "${GREEN}  ✓${NC} triplydb-integratie.md → triplydb-integration.md"
fi

if [ -f "docs/nl/shared-backend/operaton-integratie.md" ]; then
    mv docs/nl/shared-backend/operaton-integratie.md docs/nl/shared-backend/operaton-integration.md
    echo -e "${GREEN}  ✓${NC} operaton-integratie.md → operaton-integration.md"
fi

# Contributing files
if [ -f "docs/nl/contributing/documentatie-gids.md" ]; then
    mv docs/nl/contributing/documentatie-gids.md docs/nl/contributing/documentation-guide.md
    echo -e "${GREEN}  ✓${NC} documentatie-gids.md → documentation-guide.md"
fi

if [ -f "docs/nl/contributing/code-standaarden.md" ]; then
    mv docs/nl/contributing/code-standaarden.md docs/nl/contributing/code-standards.md
    echo -e "${GREEN}  ✓${NC} code-standaarden.md → code-standards.md"
fi

echo ""
echo "======================================"
echo -e "${GREEN}✅ Reorganization complete!${NC}"
echo "======================================"
echo ""
echo "Final structure:"
echo "  docs/nl/"
echo "    ├── iou-architecture/     ✓ (was iou-architectuur)"
echo "    ├── shared-backend/       ✓ (was gedeelde-backend)"
echo "    └── contributing/         ✓ (was bijdragen)"
echo ""
echo "Test now: mkdocs serve"
echo ""
echo "Expected: NO warnings about missing nav files!"
