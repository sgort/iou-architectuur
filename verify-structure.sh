#!/bin/bash

# Verify documentation structure is complete

echo "🔍 Verifying Documentation Structure"
echo "====================================="
echo ""

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

errors=0
warnings=0

check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $1"
    else
        echo -e "${RED}✗${NC} $1 - MISSING"
        ((errors++))
    fi
}

check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} $1/"
    else
        echo -e "${RED}✗${NC} $1/ - MISSING"
        ((errors++))
    fi
}

echo "Checking directory structure..."
check_dir "docs/en"
check_dir "docs/nl"
check_dir "docs/includes"
check_dir "docs/stylesheets"
echo ""

echo "Checking English files..."
check_file "docs/en/index.md"
check_file "docs/en/iou-architecture/index.md"
check_file "docs/en/cpsv-editor/index.md"
check_file "docs/en/linked-data-explorer/index.md"
check_file "docs/en/shared-backend/index.md"
check_file "docs/en/contributing/index.md"
echo ""

echo "Checking Dutch files..."
check_file "docs/nl/index.md"
check_file "docs/nl/iou-architectuur/index.md"
check_file "docs/nl/cpsv-editor/index.md"
check_file "docs/nl/linked-data-explorer/index.md"
check_file "docs/nl/gedeelde-backend/index.md"
check_file "docs/nl/bijdragen/index.md"
echo ""

# Check assets symlink
if [ -L "docs/nl/assets" ]; then
    target=$(readlink docs/nl/assets)
    if [ "$target" = "../en/assets" ]; then
        echo -e "${GREEN}✓${NC} docs/nl/assets symlink is correct (→ ../en/assets)"
    else
        echo -e "${YELLOW}⚠${NC} docs/nl/assets symlink points to: $target (expected: ../en/assets)"
        ((warnings++))
    fi
else
    echo -e "${RED}✗${NC} docs/nl/assets symlink missing"
    ((errors++))
fi
echo ""

# Count total files
en_count=$(find docs/en -name "*.md" 2>/dev/null | wc -l)
nl_count=$(find docs/nl -name "*.md" 2>/dev/null | wc -l)

echo "File counts:"
echo "  English: $en_count files"
echo "  Dutch: $nl_count files"
echo ""

# Check for common issues
echo "Checking for common issues..."

# Check for broken symlinks
broken=$(find docs -type l ! -exec test -e {} \; -print 2>/dev/null)
if [ -z "$broken" ]; then
    echo -e "${GREEN}✓${NC} No broken symlinks"
else
    echo -e "${RED}✗${NC} Broken symlinks found:"
    echo "$broken"
    ((errors++))
fi

# Check if mkdocs.yml exists
if [ -f "mkdocs.yml" ]; then
    echo -e "${GREEN}✓${NC} mkdocs.yml exists"
else
    echo -e "${RED}✗${NC} mkdocs.yml missing"
    ((errors++))
fi

# Check if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo -e "${GREEN}✓${NC} requirements.txt exists"
else
    echo -e "${RED}✗${NC} requirements.txt missing"
    ((errors++))
fi

echo ""
echo "====================================="

if [ $errors -eq 0 ] && [ $warnings -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed!${NC}"
    echo ""
    echo "You can now run: mkdocs serve"
    exit 0
elif [ $errors -eq 0 ]; then
    echo -e "${YELLOW}⚠ Passed with ${warnings} warning(s)${NC}"
    echo ""
    echo "You can run: mkdocs serve"
    exit 0
else
    echo -e "${RED}❌ Found ${errors} error(s) and ${warnings} warning(s)${NC}"
    echo ""
    echo "Please fix the errors above before running mkdocs serve"
    exit 1
fi
