#!/bin/bash

# Task 4: Docker Container Testing Script
# This script tests communication between containers

echo "=================================="
echo "Task 4: Container Testing"
echo "=================================="

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print success
success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Function to print error
error() {
    echo -e "${RED}✗ $1${NC}"
}

# Function to print info
info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    error "Docker is not installed"
    exit 1
fi
success "Docker is installed"

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    error "Docker Compose is not installed"
    exit 1
fi
success "Docker Compose is installed"

# Create sample web content
echo -e "\n[1/10] Creating sample web content..."
mkdir -p nginx-content apache-content

cat > nginx-content/index.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Nginx Server - Lab 4</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 50px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-align: center;
        }
        .container {
            background: rgba(255, 255, 255, 0.1);
            padding: 50px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }
        h1 { font-size: 3em; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Nginx Server</h1>
        <p>Security Insider Lab 4 - DDoS Defense</p>
        <p>This is the Nginx web server container</p>
    </div>
</body>
</html>
EOF
success "Created Nginx content"

cat > apache-content/index.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Apache Server - Lab 4</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 50px;
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            text-align: center;
        }
        .container {
            background: rgba(255, 255, 255, 0.1);
            padding: 50px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }
        h1 { font-size: 3em; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔥 Apache Server</h1>
        <p>Security Insider Lab 4 - DDoS Defense</p>
        <p>This is the Apache web server container</p>
    </div>
</body>
</html>
EOF
success "Created Apache content"

# Start containers
echo -e "\n[2/10] Starting Docker containers..."
docker-compose up -d
if [ $? -eq 0 ]; then
    success "Containers started"
else
    error "Failed to start containers"
    exit 1
fi

# Wait for containers to be ready
echo -e "\n[3/10] Waiting for containers to be ready..."
sleep 5

# Check container status
echo -e "\n[4/10] Checking container status..."
docker-compose ps

# Get container IPs
echo -e "\n[5/10] Getting container IP addresses..."
NGINX_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' nginx_ddos_lab)
APACHE_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' apache_ddos_lab)

info "Nginx IP: $NGINX_IP"
info "Apache IP: $APACHE_IP"

# Test 1: Ping Nginx from test client
echo -e "\n[6/10] Test: Ping Nginx from test client..."
docker exec test_client_ddos_lab ping -c 3 nginx-server > /dev/null 2>&1
if [ $? -eq 0 ]; then
    success "Can ping Nginx server"
else
    error "Cannot ping Nginx server"
fi

# Test 2: Ping Apache from test client
echo -e "\n[7/10] Test: Ping Apache from test client..."
docker exec test_client_ddos_lab ping -c 3 apache-server > /dev/null 2>&1
if [ $? -eq 0 ]; then
    success "Can ping Apache server"
else
    error "Cannot ping Apache server"
fi

# Test 3: HTTP request to Nginx
echo -e "\n[8/10] Test: HTTP request to Nginx..."
docker exec test_client_ddos_lab curl -s http://nginx-server > /dev/null
if [ $? -eq 0 ]; then
    success "Can access Nginx via HTTP"
    info "Try: http://localhost:8080 in your browser"
else
    error "Cannot access Nginx via HTTP"
fi

# Test 4: HTTP request to Apache
echo -e "\n[9/10] Test: HTTP request to Apache..."
docker exec test_client_ddos_lab curl -s http://apache-server > /dev/null
if [ $? -eq 0 ]; then
    success "Can access Apache via HTTP"
    info "Try: http://localhost:8081 in your browser"
else
    error "Cannot access Apache via HTTP"
fi

# Network analysis
echo -e "\n[10/10] Network analysis..."
info "Checking network connectivity..."
docker exec test_client_ddos_lab ip addr show
docker exec test_client_ddos_lab ip route show

echo -e "\n=================================="
echo "Summary"
echo "=================================="
success "Container setup complete!"
echo ""
echo "📊 Container URLs:"
echo "   Nginx:  http://localhost:8080"
echo "   Apache: http://localhost:8081"
echo ""
echo "🔧 Useful commands:"
echo "   View logs:     docker-compose logs -f"
echo "   Stop all:      docker-compose down"
echo "   Shell access:  docker exec -it test_client_ddos_lab bash"
echo ""
echo "🧪 Inside test client container, try:"
echo "   ping nginx-server"
echo "   ping apache-server"
echo "   curl http://nginx-server"
echo "   curl http://apache-server"
echo "   traceroute nginx-server"
echo ""
echo "📸 Take screenshots for your report!"
echo "=================================="
