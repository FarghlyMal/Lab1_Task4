#!/bin/bash

# Submission Preparation Script for Lab 4
# This script helps you prepare your final submission

echo "╔════════════════════════════════════════════════════════════╗"
echo "║         Lab 4 Submission Preparation Checklist            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
REQUIRED_OK=0
REQUIRED_TOTAL=0
OPTIONAL_OK=0
OPTIONAL_TOTAL=0

# Function to check required item
check_required() {
    REQUIRED_TOTAL=$((REQUIRED_TOTAL + 1))
    if [ "$1" = true ]; then
        echo -e "${GREEN}✓${NC} $2"
        REQUIRED_OK=$((REQUIRED_OK + 1))
    else
        echo -e "${RED}✗${NC} $2"
    fi
}

# Function to check optional item
check_optional() {
    OPTIONAL_TOTAL=$((OPTIONAL_TOTAL + 1))
    if [ "$1" = true ]; then
        echo -e "${GREEN}✓${NC} $2"
        OPTIONAL_OK=$((OPTIONAL_OK + 1))
    else
        echo -e "${YELLOW}○${NC} $2"
    fi
}

echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}REQUIRED FILES${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"

# Check required files
check_required "[ -f README.md ]" "README.md - Project documentation"
check_required "[ -f requirements.txt ]" "requirements.txt - Python dependencies"
check_required "[ -f ddos_detection.py ]" "ddos_detection.py - Main detection system"
check_required "[ -f dashboard_app.py ]" "dashboard_app.py - Web dashboard"
check_required "[ -f docker-compose.yml ]" "docker-compose.yml - Container orchestration"
check_required "[ -f setup_xdp_wsl.sh ]" "setup_xdp_wsl.sh - XDP setup script"
check_required "[ -d templates ]" "templates/ - HTML templates directory"
check_required "[ -f templates/dashboard.html ]" "templates/dashboard.html - Dashboard UI"

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}OPTIONAL/HELPFUL FILES${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"

check_optional "[ -f test_xdp_filter.sh ]" "test_xdp_filter.sh - XDP testing script"
check_optional "[ -f test_docker.sh ]" "test_docker.sh - Docker testing script"
check_optional "[ -f traffic_generator.py ]" "traffic_generator.py - Traffic generator"
check_optional "[ -f quick_start.sh ]" "quick_start.sh - Quick start guide"
check_optional "[ -f .gitignore ]" ".gitignore - Git ignore file"
check_optional "[ -f Dockerfile.detector ]" "Dockerfile.detector - Detector container"

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}SCREENSHOTS${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"

# Check screenshot directories
check_required "[ -d screenshots ]" "screenshots/ - Main directory"
check_required "[ -d screenshots/task1 ]" "screenshots/task1/ - Task 1 screenshots"
check_required "[ -d screenshots/task2 ]" "screenshots/task2/ - Task 2 screenshots"
check_required "[ -d screenshots/task3 ]" "screenshots/task3/ - Task 3 screenshots"
check_required "[ -d screenshots/task4 ]" "screenshots/task4/ - Task 4 screenshots"

# Count screenshots
if [ -d screenshots ]; then
    TASK1_COUNT=$(find screenshots/task1 -type f 2>/dev/null | wc -l)
    TASK2_COUNT=$(find screenshots/task2 -type f 2>/dev/null | wc -l)
    TASK3_COUNT=$(find screenshots/task3 -type f 2>/dev/null | wc -l)
    TASK4_COUNT=$(find screenshots/task4 -type f 2>/dev/null | wc -l)
    
    echo ""
    echo "Screenshot counts:"
    check_required "[ $TASK1_COUNT -ge 5 ]" "Task 1: $TASK1_COUNT screenshots (minimum 5)"
    check_required "[ $TASK2_COUNT -ge 5 ]" "Task 2: $TASK2_COUNT screenshots (minimum 5)"
    check_required "[ $TASK3_COUNT -ge 4 ]" "Task 3: $TASK3_COUNT screenshots (minimum 4)"
    check_required "[ $TASK4_COUNT -ge 6 ]" "Task 4: $TASK4_COUNT screenshots (minimum 6)"
fi

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}REPORT${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"

# Check for report (might not be in repo)
if [ -f G*.Report4.pdf ]; then
    REPORT_FILE=$(ls G*.Report4.pdf | head -1)
    REPORT_SIZE=$(du -h "$REPORT_FILE" | cut -f1)
    REPORT_PAGES=$(pdfinfo "$REPORT_FILE" 2>/dev/null | grep Pages | awk '{print $2}')
    
    check_required "true" "Report found: $REPORT_FILE ($REPORT_SIZE)"
    
    if [ -n "$REPORT_PAGES" ]; then
        check_required "[ $REPORT_PAGES -ge 15 ] && [ $REPORT_PAGES -le 20 ]" \
            "Report pages: $REPORT_PAGES (should be 15-20)"
    fi
else
    check_required "false" "Report: GX.Report4.pdf (not found - create before submission)"
fi

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}CODE QUALITY${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"

# Check if code runs
if [ -f ddos_detection.py ]; then
    python3 -c "import py_compile; py_compile.compile('ddos_detection.py', doraise=True)" 2>/dev/null
    check_optional "[ $? -eq 0 ]" "ddos_detection.py - Syntax check"
fi

if [ -f dashboard_app.py ]; then
    python3 -c "import py_compile; py_compile.compile('dashboard_app.py', doraise=True)" 2>/dev/null
    check_optional "[ $? -eq 0 ]" "dashboard_app.py - Syntax check"
fi

if [ -f traffic_generator.py ]; then
    python3 -c "import py_compile; py_compile.compile('traffic_generator.py', doraise=True)" 2>/dev/null
    check_optional "[ $? -eq 0 ]" "traffic_generator.py - Syntax check"
fi

# Check for comments in code
if [ -f ddos_detection.py ]; then
    COMMENT_COUNT=$(grep -c "^[[:space:]]*#" ddos_detection.py)
    check_optional "[ $COMMENT_COUNT -gt 50 ]" "Code comments: $COMMENT_COUNT lines (good documentation)"
fi

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}GIT REPOSITORY${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"

if [ -d .git ]; then
    check_optional "true" "Git repository initialized"
    
    # Check if there are commits
    COMMIT_COUNT=$(git rev-list --count HEAD 2>/dev/null)
    check_optional "[ $COMMIT_COUNT -gt 0 ]" "Commits: $COMMIT_COUNT"
    
    # Check if there's a remote
    REMOTE=$(git remote -v 2>/dev/null | grep origin | head -1 | awk '{print $2}')
    if [ -n "$REMOTE" ]; then
        check_optional "true" "Remote repository: $REMOTE"
    else
        check_optional "false" "Remote repository not configured"
    fi
else
    check_optional "false" "Git repository not initialized"
    echo -e "  ${YELLOW}Run: git init && git add . && git commit -m 'Initial commit'${NC}"
fi

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}SUMMARY${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"

REQUIRED_PERCENT=$((REQUIRED_OK * 100 / REQUIRED_TOTAL))
OPTIONAL_PERCENT=$((OPTIONAL_OK * 100 / OPTIONAL_TOTAL))

echo ""
echo "Required items: $REQUIRED_OK/$REQUIRED_TOTAL ($REQUIRED_PERCENT%)"
echo "Optional items: $OPTIONAL_OK/$OPTIONAL_TOTAL ($OPTIONAL_PERCENT%)"
echo ""

if [ $REQUIRED_OK -eq $REQUIRED_TOTAL ]; then
    echo -e "${GREEN}✓ All required items complete!${NC}"
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║           READY FOR SUBMISSION! 🎉                         ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
else
    MISSING=$((REQUIRED_TOTAL - REQUIRED_OK))
    echo -e "${RED}✗ $MISSING required items missing${NC}"
    echo ""
    echo -e "${YELLOW}Please complete all required items before submission.${NC}"
fi

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}SUBMISSION INSTRUCTIONS${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""
echo "1. Create GitHub repository:"
echo "   git init"
echo "   git add ."
echo "   git commit -m 'Lab 4 - DDoS Defense'"
echo "   git branch -M main"
echo "   git remote add origin <your-github-repo-url>"
echo "   git push -u origin main"
echo ""
echo "2. Prepare report:"
echo "   • File name: GX.Report4.pdf (X = your group number)"
echo "   • Length: 15-20 pages"
echo "   • Include all screenshots"
echo "   • Add GitHub repository link in report"
echo ""
echo "3. Send email to: tf@sec.uni-passau.de"
echo "   Subject: Lab-2025: matriculation ID-1, matriculation ID-2"
echo "   • Reply to same email thread from Lab 1"
echo "   • Attach: GX.Report4.pdf"
echo "   • Include: GitHub repository link"
echo ""
echo "4. Deadline: December 3, 2024"
echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""
echo "Good luck! 🚀"
