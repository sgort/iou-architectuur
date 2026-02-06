#!/bin/bash

# Find and Fix Broken Links in RONL Business API Docs
# Finds markdown links to missing files and optionally comments them out

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Mode: report or fix
MODE="${1:-report}"

if [[ "$MODE" != "report" && "$MODE" != "fix" ]]; then
    echo "Usage: $0 [report|fix]"
    echo ""
    echo "  report (default) - Show broken links without modifying files"
    echo "  fix              - Comment out broken links in markdown files"
    exit 1
fi

echo -e "${BLUE}🔍 Checking for Broken Links in RONL Business API Documentation${NC}"
echo "======================================================================="
echo "Mode: ${MODE}"
echo ""

# Check we're in the right directory
if [ ! -d "docs/en/ronl-business-api" ]; then
    echo -e "${RED}Error: docs/en/ronl-business-api not found!${NC}"
    echo "Please run this script from the iou-architectuur root directory."
    exit 1
fi

# Counters
total_files=0
files_with_issues=0
total_broken_links=0

# Temporary file for processing
temp_file=$(mktemp)

# Function to check if a file exists relative to a base
check_link_exists() {
    local base_file=$1
    local link=$2
    local base_dir=$(dirname "$base_file")
    
    # Handle relative links
    if [[ "$link" == ../* ]] || [[ "$link" != http* ]]; then
        # Resolve relative path
        local target_path=$(cd "$base_dir" && realpath --relative-to="." "$link" 2>/dev/null || echo "INVALID")
        
        if [ "$target_path" = "INVALID" ]; then
            return 1
        fi
        
        # Check if file exists
        if [ -f "$base_dir/$link" ]; then
            return 0
        else
            return 1
        fi
    fi
    
    # External links always pass
    return 0
}

# Process each markdown file
echo -e "${BLUE}Scanning files...${NC}"
echo ""

while IFS= read -r file; do
    ((total_files++))
    
    file_has_issues=0
    file_broken_count=0
    
    # Extract markdown links: [text](url)
    # Using grep to find lines with markdown links
    while IFS= read -r line_num; do
        line=$(sed -n "${line_num}p" "$file")
        
        # Extract all [text](url) patterns from this line
        while [[ "$line" =~ \[([^\]]+)\]\(([^\)]+)\) ]]; do
            link_text="${BASH_REMATCH[1]}"
            link_url="${BASH_REMATCH[2]}"
            
            # Skip anchors and external links
            if [[ "$link_url" == \#* ]] || [[ "$link_url" == http* ]] || [[ "$link_url" == mailto:* ]]; then
                # Remove matched part and continue
                line="${line#*\](*\)}"
                continue
            fi
            
            # Check if link target exists
            if ! check_link_exists "$file" "$link_url"; then
                if [ $file_has_issues -eq 0 ]; then
                    echo -e "${YELLOW}File: ${file}${NC}"
                    file_has_issues=1
                    ((files_with_issues++))
                fi
                
                echo -e "${RED}  ✗${NC} Line ${line_num}: [${link_text}](${link_url})"
                ((file_broken_count++))
                ((total_broken_links++))
                
                # Fix mode: comment out the link
                if [ "$MODE" = "fix" ]; then
                    # Replace [text](url) with <!-- [text](url) --> (keeping it visible but commented)
                    sed -i "${line_num}s|\[${link_text}\](${link_url})|<!-- [${link_text}](${link_url}) BROKEN LINK -->|g" "$file"
                fi
            fi
            
            # Remove matched part and continue searching this line
            line="${line#*\](*\)}"
        done
    done < <(grep -n '\[.*\](.*)'  "$file" | cut -d: -f1)
    
    if [ $file_has_issues -eq 1 ]; then
        echo -e "  ${YELLOW}Found ${file_broken_count} broken link(s)${NC}"
        echo ""
    fi
    
done < <(find docs/en/ronl-business-api -name "*.md" -type f)

# Summary
echo "======================================================================="
echo -e "${BLUE}Summary${NC}"
echo "-----------------------------------------------------------------------"
echo "Files scanned:           $total_files"
echo "Files with broken links: $files_with_issues"
echo "Total broken links:      $total_broken_links"
echo ""

if [ $total_broken_links -eq 0 ]; then
    echo -e "${GREEN}✅ No broken links found!${NC}"
elif [ "$MODE" = "report" ]; then
    echo -e "${YELLOW}⚠️  Found $total_broken_links broken link(s)${NC}"
    echo ""
    echo "To fix these automatically, run:"
    echo "  $0 fix"
    echo ""
    echo "This will comment out broken links like:"
    echo "  [text](url) → <!-- [text](url) BROKEN LINK -->"
else
    echo -e "${GREEN}✅ Fixed $total_broken_links broken link(s)${NC}"
    echo ""
    echo "Broken links have been commented out."
    echo "Review the changes with: git diff"
fi

# Cleanup
rm -f "$temp_file"
