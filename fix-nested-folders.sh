#!/bin/bash

# Fix nested folder structure and update homepage links

set -e

echo "🔧 Fixing nested folder structure"
echo "================================="
echo ""

# Fix nested structures by moving content up and removing old folder

# Fix iou-architecture
if [ -d "docs/nl/iou-architecture/iou-architectuur" ]; then
    echo "Fixing iou-architecture..."
    mv docs/nl/iou-architecture/iou-architectuur/* docs/nl/iou-architecture/
    rmdir docs/nl/iou-architecture/iou-architectuur
    echo "  ✓ Fixed"
fi

# Fix shared-backend
if [ -d "docs/nl/shared-backend/gedeelde-backend" ]; then
    echo "Fixing shared-backend..."
    mv docs/nl/shared-backend/gedeelde-backend/* docs/nl/shared-backend/
    rmdir docs/nl/shared-backend/gedeelde-backend
    echo "  ✓ Fixed"
fi

# Fix contributing
if [ -d "docs/nl/contributing/bijdragen" ]; then
    echo "Fixing contributing..."
    mv docs/nl/contributing/bijdragen/* docs/nl/contributing/
    rmdir docs/nl/contributing/bijdragen
    echo "  ✓ Fixed"
fi

echo ""
echo "Renaming files to match English structure..."

# IOU Architecture
if [ -f "docs/nl/iou-architecture/ontologische-architectuur.md" ]; then
    mv docs/nl/iou-architecture/ontologische-architectuur.md docs/nl/iou-architecture/ontological-architecture.md
    echo "  ✓ ontologische-architectuur.md → ontological-architecture.md"
fi

if [ -f "docs/nl/iou-architecture/implementatie-architectuur.md" ]; then
    mv docs/nl/iou-architecture/implementatie-architectuur.md docs/nl/iou-architecture/implementation-architecture.md
    echo "  ✓ implementatie-architectuur.md → implementation-architecture.md"
fi

if [ -f "docs/nl/iou-architecture/roadmap-evaluatie.md" ]; then
    mv docs/nl/iou-architecture/roadmap-evaluatie.md docs/nl/iou-architecture/roadmap-evaluation.md
    echo "  ✓ roadmap-evaluatie.md → roadmap-evaluation.md"
fi

# Shared Backend
if [ -f "docs/nl/shared-backend/api-documentatie.md" ]; then
    mv docs/nl/shared-backend/api-documentatie.md docs/nl/shared-backend/api-documentation.md
    echo "  ✓ api-documentatie.md → api-documentation.md"
fi

if [ -f "docs/nl/shared-backend/triplydb-integratie.md" ]; then
    mv docs/nl/shared-backend/triplydb-integratie.md docs/nl/shared-backend/triplydb-integration.md
    echo "  ✓ triplydb-integratie.md → triplydb-integration.md"
fi

if [ -f "docs/nl/shared-backend/operaton-integratie.md" ]; then
    mv docs/nl/shared-backend/operaton-integratie.md docs/nl/shared-backend/operaton-integration.md
    echo "  ✓ operaton-integratie.md → operaton-integration.md"
fi

# Contributing
if [ -f "docs/nl/contributing/documentatie-gids.md" ]; then
    mv docs/nl/contributing/documentatie-gids.md docs/nl/contributing/documentation-guide.md
    echo "  ✓ documentatie-gids.md → documentation-guide.md"
fi

if [ -f "docs/nl/contributing/code-standaarden.md" ]; then
    mv docs/nl/contributing/code-standaarden.md docs/nl/contributing/code-standards.md
    echo "  ✓ code-standaarden.md → code-standards.md"
fi

echo ""
echo "Updating links in nl/index.md..."

# Fix links in Dutch homepage
sed -i 's|iou-architectuur/index.md|iou-architecture/index.md|g' docs/nl/index.md
sed -i 's|gedeelde-backend/index.md|shared-backend/index.md|g' docs/nl/index.md

echo "  ✓ Updated homepage links"

echo ""
echo "================================="
echo "✅ All fixed!"
echo "================================="
echo ""
echo "Structure is now:"
echo "  docs/nl/"
echo "    ├── iou-architecture/      ✓"
echo "    ├── cpsv-editor/           ✓"
echo "    ├── linked-data-explorer/  ✓"
echo "    ├── shared-backend/        ✓"
echo "    └── contributing/          ✓"
echo ""
echo "Test: mkdocs serve"
echo ""
echo "Expected: Only 'includes/abbreviations.md' warning (which is OK)"
