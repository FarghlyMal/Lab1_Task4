#!/bin/bash

# File Verification Script
# Run this to verify all Lab 4 files are downloaded correctly

echo "╔════════════════════════════════════════════════════════════╗"
echo "║         Lab 4 Files Verification                          ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Counter
FOUND=0
MISSING=0

check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $1 ($(du -h "$1" | cut -f1))"
        FOUND=$((FOUND + 1))
    else
        echo -e "${RED}✗${NC} $1 - MISSING!"
        MISSING=$((MISSING + 1))
    fi
}

echo "Checking Shell Scripts:"
check_file "setup_xdp_wsl.sh"
check_file "test_xdp_filter.sh"
check_file "test_docker.sh"
check_file "quick_start.sh"
check_file "check_submission.sh"

echo ""
echo "Checking Python Files:"
check_file "ddos_detection.py"
check_file "dashboard_app.py"
check_file "traffic_generator.py"

echo ""
echo "Checking Configuration Files:"
check_file "requirements.txt"
check_file "docker-compose.yml"
check_file "Dockerfile.detector"
check_file ".gitignore"

echo ""
echo "Checking Documentation:"
check_file "README.md"
check_file "GETTING_STARTED.md"
check_file "FILE_LIST.md"
check_file "PROJECT_SUMMARY.md"

echo ""
echo "Checking Directories:"
if [ -d "templates" ]; then
    echo -e "${GREEN}✓${NC} templates/"
    FOUND=$((FOUND + 1))
    check_file "templates/dashboard.html"
else
    echo -e "${RED}✗${NC} templates/ - MISSING!"
    MISSING=$((MISSING + 1))
fi

echo ""
echo "════════════════════════════════════════════════════════════"
echo "Summary:"
echo "  Found: $FOUND files"
echo "  Missing: $MISSING files"
echo ""

if [ $MISSING -eq 0 ]; then
    echo -e "${GREEN}✓ All files present! You're ready to go!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Make scripts executable: chmod +x *.sh"
    echo "  2. Read: cat README.md"
    echo "  3. Start: ./quick_start.sh"
else
    echo -e "${RED}✗ Some files are missing. Please download all files.${NC}"
fi

echo "════════════════════════════════════════════════════════════"
