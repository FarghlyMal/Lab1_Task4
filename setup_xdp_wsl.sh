#!/bin/bash

# Lab 4 - XDP Setup Script for WSL
# This script sets up xdp-tools and checks for compatibility

echo "=================================="
echo "Lab 4: XDP/eBPF Setup for WSL"
echo "=================================="

# Check if running on WSL
if grep -qi microsoft /proc/version; then
    echo "✓ Running on WSL"
else
    echo "⚠ Not running on WSL - some steps may differ"
fi

# Update system
echo -e "\n[1/8] Updating system packages..."
sudo apt-get update

# Install dependencies
echo -e "\n[2/8] Installing dependencies..."
sudo apt-get install -y \
    clang \
    llvm \
    libelf-dev \
    libpcap-dev \
    gcc-multilib \
    build-essential \
    linux-tools-common \
    linux-tools-generic \
    pkg-config \
    m4 \
    libz-dev \
    git

# Check kernel version
echo -e "\n[3/8] Checking kernel version..."
KERNEL_VERSION=$(uname -r)
echo "Kernel version: $KERNEL_VERSION"

# Check for BPF support
echo -e "\n[4/8] Checking BPF support..."
if [ -f /proc/config.gz ]; then
    zcat /proc/config.gz | grep -i "CONFIG_BPF" || echo "BPF config not found in /proc/config.gz"
else
    echo "⚠ /proc/config.gz not available"
    echo "Checking for BPF syscall support..."
    if [ -e /proc/sys/kernel/unprivileged_bpf_disabled ]; then
        echo "✓ BPF syscall appears to be supported"
    else
        echo "⚠ BPF support unclear"
    fi
fi

# Install libbpf
echo -e "\n[5/8] Installing libbpf..."
cd /tmp
if [ -d "libbpf" ]; then
    rm -rf libbpf
fi
git clone https://github.com/libbpf/libbpf.git
cd libbpf/src
sudo make install
sudo ldconfig

# Clone xdp-tools
echo -e "\n[6/8] Cloning xdp-tools..."
cd ~/
if [ -d "xdp-tools" ]; then
    echo "xdp-tools directory exists, removing..."
    rm -rf xdp-tools
fi
git clone --recurse-submodules https://github.com/xdp-project/xdp-tools.git
cd xdp-tools

# Build xdp-tools
echo -e "\n[7/8] Building xdp-tools..."
./configure
make

# Check if build succeeded
if [ $? -eq 0 ]; then
    echo "✓ Build successful"
    
    # Optional: Install system-wide
    echo -e "\n[8/8] Installing xdp-tools system-wide..."
    sudo make install
    
    echo -e "\n=================================="
    echo "Setup Complete!"
    echo "=================================="
    echo "xdp-tools installed at: ~/xdp-tools"
    echo ""
    echo "Key tools available:"
    echo "  - xdp-filter: ~/xdp-tools/xdp-filter/xdp-filter"
    echo "  - xdp-dump: ~/xdp-tools/xdp-dump/xdp-dump"
    echo ""
    echo "To test, try:"
    echo "  sudo ~/xdp-tools/xdp-filter/xdp-filter --help"
else
    echo "✗ Build failed - check errors above"
    exit 1
fi

# Check available network interfaces
echo -e "\n=================================="
echo "Available Network Interfaces:"
echo "=================================="
ip link show

echo -e "\n⚠ IMPORTANT WSL NOTES:"
echo "1. XDP requires root privileges (use sudo)"
echo "2. WSL interfaces may have limited XDP support"
echo "3. Use 'eth0' or available interface for testing"
echo "4. Some XDP features may not work due to WSL limitations"
