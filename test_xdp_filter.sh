#!/bin/bash

# Task 1: XDP Filter Testing Script
# This script demonstrates xdp-filter functionality

echo "=================================="
echo "Task 1: XDP Filter Testing"
echo "=================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "⚠ Please run as root (sudo)"
    exit 1
fi

# Get network interface
echo -e "\nAvailable interfaces:"
ip link show | grep -E "^[0-9]+:" | awk '{print $2}' | sed 's/://g'

echo -e "\nEnter interface name (e.g., eth0):"
read IFACE

if [ -z "$IFACE" ]; then
    echo "No interface specified, using eth0"
    IFACE="eth0"
fi

# Check if interface exists
if ! ip link show "$IFACE" &> /dev/null; then
    echo "✗ Interface $IFACE does not exist"
    exit 1
fi

echo -e "\n=================================="
echo "Test 1: Load XDP Filter"
echo "=================================="
echo "Loading XDP filter on interface: $IFACE"
xdp-filter load $IFACE

echo -e "\n=================================="
echo "Test 2: Show XDP Filter Status"
echo "=================================="
xdp-filter status $IFACE

echo -e "\n=================================="
echo "Test 3: Block Specific IP Address"
echo "=================================="
# Example: Block traffic from 192.168.1.100
echo "Blocking IP: 192.168.1.100"
xdp-filter ip $IFACE -m src -a deny 192.168.1.100

echo -e "\n=================================="
echo "Test 4: Block Port"
echo "=================================="
# Example: Block port 8080
echo "Blocking port: 8080"
xdp-filter port $IFACE -m src -a deny 8080

echo -e "\n=================================="
echo "Test 5: List Current Rules"
echo "=================================="
xdp-filter status $IFACE

echo -e "\n=================================="
echo "Test 6: Poll Statistics"
echo "=================================="
echo "Showing statistics for 10 seconds..."
timeout 10 xdp-filter poll $IFACE

echo -e "\n=================================="
echo "Test 7: Unload XDP Filter"
echo "=================================="
echo "Unloading XDP filter from $IFACE"
xdp-filter unload $IFACE

echo -e "\n=================================="
echo "Testing Complete!"
echo "=================================="
echo ""
echo "📸 Take screenshots of:"
echo "  1. xdp-filter load output"
echo "  2. xdp-filter status output"
echo "  3. Rule addition outputs"
echo "  4. Statistics from poll"
echo ""
echo "⚠ Note: On WSL, some operations may fail due to"
echo "   limited kernel support. Document any errors."
