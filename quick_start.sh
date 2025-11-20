#!/bin/bash

# Quick Start Guide for Lab 4
# Run this script to get started quickly

cat << 'EOF'
╔════════════════════════════════════════════════════════════╗
║         Security Insider Lab 4 - Quick Start              ║
║              DDoS Defense using eBPF/XDP                  ║
╚════════════════════════════════════════════════════════════╝

This script will help you get started with Lab 4 quickly.

PREREQUISITES:
✓ WSL2 with Ubuntu 22.04
✓ At least 4GB free disk space
✓ Internet connection
✓ Sudo privileges

What this script will do:
1. Check system requirements
2. Install dependencies
3. Set up the environment
4. Run basic tests
5. Provide next steps

Press Enter to continue, or Ctrl+C to cancel...
EOF

read -r

echo ""
echo "═══════════════════════════════════════════════════════"
echo "Step 1: Checking System Requirements"
echo "═══════════════════════════════════════════════════════"

# Check if WSL
if grep -qi microsoft /proc/version; then
    echo "✓ Running on WSL"
else
    echo "⚠ Not running on WSL - some features may differ"
fi

# Check kernel version
KERNEL=$(uname -r)
echo "✓ Kernel version: $KERNEL"

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "⚠ Please don't run this script as root (we'll ask for sudo when needed)"
    exit 1
fi

# Check disk space
SPACE=$(df -h . | awk 'NR==2 {print $4}')
echo "✓ Available disk space: $SPACE"

echo ""
echo "═══════════════════════════════════════════════════════"
echo "Step 2: Installing Dependencies"
echo "═══════════════════════════════════════════════════════"

# Update package list
echo "Updating package list..."
sudo apt update -qq

# Install essential tools
echo "Installing essential tools..."
sudo apt install -y -qq \
    python3 \
    python3-pip \
    git \
    curl \
    build-essential \
    2>/dev/null

echo "✓ Essential tools installed"

# Install Python packages
echo "Installing Python packages (this may take a few minutes)..."
pip3 install -q scapy numpy flask flask-cors 2>/dev/null
echo "✓ Python packages installed"

echo ""
echo "═══════════════════════════════════════════════════════"
echo "Step 3: Setting Up Project"
echo "═══════════════════════════════════════════════════════"

# Make scripts executable
if [ -f "setup_xdp_wsl.sh" ]; then
    chmod +x setup_xdp_wsl.sh
    chmod +x test_xdp_filter.sh
    chmod +x test_docker.sh
    echo "✓ Made scripts executable"
fi

# Create necessary directories
mkdir -p logs screenshots/{task1,task2,task3,task4}
echo "✓ Created directory structure"

echo ""
echo "═══════════════════════════════════════════════════════"
echo "Step 4: Testing Basic Functionality"
echo "═══════════════════════════════════════════════════════"

# Test Python imports
echo "Testing Python imports..."
python3 << PYEOF
try:
    import scapy
    import flask
    import numpy
    print("✓ All Python packages working")
except ImportError as e:
    print(f"✗ Import error: {e}")
PYEOF

# Check network interfaces
echo ""
echo "Available network interfaces:"
ip link show | grep -E "^[0-9]+:" | awk '{print "  " $2}' | sed 's/://g'

# Test sudo access
echo ""
echo "Testing sudo access (you may need to enter password)..."
if sudo -v; then
    echo "✓ Sudo access confirmed"
else
    echo "✗ Sudo access required for this lab"
fi

echo ""
echo "═══════════════════════════════════════════════════════"
echo "Setup Complete!"
echo "═══════════════════════════════════════════════════════"
echo ""
echo "📚 NEXT STEPS:"
echo ""
echo "TASK 1: XDP Configuration"
echo "  Run: sudo ./setup_xdp_wsl.sh"
echo "  Then: sudo ./test_xdp_filter.sh"
echo ""
echo "TASK 2: Real-Time Detection"
echo "  Run: sudo python3 ddos_detection.py eth0"
echo "  (Replace eth0 with your interface)"
echo ""
echo "TASK 3: Frontend Dashboard"
echo "  Terminal 1: sudo python3 ddos_detection.py eth0"
echo "  Terminal 2: python3 dashboard_app.py"
echo "  Browser: http://localhost:5000"
echo ""
echo "TASK 4: Docker Containers"
echo "  Run: ./test_docker.sh"
echo ""
echo "📖 For detailed instructions, read: README.md"
echo "   Use: cat README.md | less"
echo ""
echo "💡 TIPS:"
echo "  • Always use sudo for network capture tools"
echo "  • Use 'eth0' or check your interface with: ip link show"
echo "  • Take screenshots of everything for your report"
echo "  • WSL has XDP limitations - document any errors"
echo ""
echo "❓ NEED HELP?"
echo "  Email: tf@sec.uni-passau.de"
echo "  Check: README.md for troubleshooting"
echo ""
echo "Good luck! 🚀"
echo "═══════════════════════════════════════════════════════"
