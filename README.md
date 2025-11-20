# Security Insider Lab 4: DDoS Defense using eBPF/XDP

**Talaya Farasat - Passau Institute of Digital Security**

This repository contains the complete implementation for Lab 4, focusing on DDoS detection and mitigation using eBPF/XDP, machine learning, and containerization.

## 📋 Table of Contents

- [Overview](#overview)
- [WSL-Specific Setup](#wsl-specific-setup)
- [Task 1: XDP Configuration](#task-1-xdp-configuration)
- [Task 2: Real-Time Detection Cycle](#task-2-real-time-detection-cycle)
- [Task 3: Frontend Interface](#task-3-frontend-interface)
- [Task 4: Containerization](#task-4-containerization)
- [Running the Complete System](#running-the-complete-system)
- [Troubleshooting](#troubleshooting)
- [Report Guidelines](#report-guidelines)

---

## 🎯 Overview

This lab implements a complete DDoS detection and mitigation system with:
- **Packet Capture**: Real-time network traffic monitoring
- **Flow Analysis**: Statistical feature extraction from network flows
- **ML Classification**: Machine learning-based attack detection
- **Automated Mitigation**: XDP/eBPF kernel-level filtering
- **Web Dashboard**: Real-time visualization of detections
- **Containerization**: Docker-based isolated testing environment

---

## 💻 WSL-Specific Setup

### Prerequisites

```bash
# Check WSL version
wsl --version

# Ensure you're on WSL2 (required for better kernel support)
wsl --set-version Ubuntu 2
```

### Important WSL Limitations

⚠️ **XDP Limitations on WSL**:
- WSL2 has limited eBPF/XDP support
- Network interfaces are virtualized
- Some XDP features may not work
- Fallback to iptables is implemented

### Initial Setup

```bash
# Update WSL kernel (run in PowerShell as Administrator)
wsl --update

# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Git if not already installed
sudo apt install git -y
```

---

## 📦 Installation

### 1. Clone/Download the Project

```bash
cd ~
# If you have this as a git repo:
git clone <your-repo-url> lab4-ddos-defense
cd lab4-ddos-defense

# Or if you have files directly:
mkdir lab4-ddos-defense
cd lab4-ddos-defense
# Copy all files here
```

### 2. Make Scripts Executable

```bash
chmod +x setup_xdp_wsl.sh
chmod +x test_xdp_filter.sh
chmod +x test_docker.sh
```

### 3. Run Setup Script

```bash
# This will install all dependencies
sudo ./setup_xdp_wsl.sh
```

**Expected Duration**: 10-15 minutes

### 4. Install Python Dependencies

```bash
# Install pip if needed
sudo apt install python3-pip -y

# Install required Python packages
pip3 install -r requirements.txt

# Verify installation
python3 -c "import scapy; import flask; print('All packages installed successfully!')"
```

---

## Task 1: XDP Configuration

### Objective
Configure and test xdp-tools (xdp-filter and xdp-dump)

### Steps

1. **Verify Installation**
   ```bash
   # Check if xdp-filter is available
   sudo xdp-filter --help
   
   # Check available network interfaces
   ip link show
   ```

2. **Run XDP Filter Tests**
   ```bash
   # Run the test script (will prompt for interface)
   sudo ./test_xdp_filter.sh
   
   # Or specify interface directly:
   sudo ./test_xdp_filter.sh eth0
   ```

3. **Manual XDP Commands** (for screenshots)
   ```bash
   # Load XDP filter on interface
   sudo xdp-filter load eth0
   
   # Check status
   sudo xdp-filter status eth0
   
   # Block an IP address
   sudo xdp-filter ip eth0 -m src -a deny 192.168.1.100
   
   # Block a port
   sudo xdp-filter port eth0 -m src -a deny 8080
   
   # View statistics
   sudo xdp-filter poll eth0
   
   # Unload filter
   sudo xdp-filter unload eth0
   ```

4. **XDP Dump Usage**
   ```bash
   # Capture packets with XDP
   sudo xdp-dump -i eth0
   
   # Capture and save to pcap
   sudo xdp-dump -i eth0 -w capture.pcap
   
   # Capture with filter
   sudo xdp-dump -i eth0 -x "tcp port 80"
   ```

### Expected Outputs

✅ **Success Indicators**:
- XDP filter loads without errors
- Rules are added successfully
- Statistics show packet processing

⚠️ **Common WSL Issues**:
- "Operation not supported" - XDP may not work on WSL interfaces
- Fallback to iptables is automatic in our implementation
- Document any errors in your report

### Screenshots Needed
1. `xdp-filter --help` output
2. `xdp-filter load` command
3. `xdp-filter status` showing loaded program
4. Rule addition outputs
5. `xdp-filter poll` statistics
6. Any error messages (important for WSL context)

---

## Task 2: Real-Time Detection Cycle

### Architecture

```
[Packet Capture] → [FlowMeter] → [ML Classifier] → [XDP Filter]
     (Scapy)         (Feature          (Model)        (Kernel)
                    Extraction)
```

### Implementation Options

**Best Case** (Ideal):
- Classifier at kernel level ✓
- XDP filter at kernel level ✓

**Acceptable Case** (Practical on WSL):
- Classifier at user level ✓
- XDP filter with iptables fallback ✓

### Running the System

1. **Prepare ML Model** (Optional)
   ```bash
   # If you have a trained model from Lab 2/3:
   # Place it in the current directory as: model.pkl
   ```

2. **Start Detection System**
   ```bash
   # Basic usage (no ML model, uses heuristics)
   sudo python3 ddos_detection.py eth0
   
   # With ML model
   sudo python3 ddos_detection.py eth0 model.pkl
   
   # The system will:
   # - Start capturing packets
   # - Extract flow features
   # - Classify traffic
   # - Block malicious IPs
   # - Log all detections
   ```

3. **Generate Test Traffic** (in another terminal)
   ```bash
   # Normal traffic
   ping 8.8.8.8 -c 100
   
   # HTTP requests
   while true; do curl http://example.com; sleep 1; done
   
   # High-volume traffic (simulated DDoS)
   # Install hping3 first:
   sudo apt install hping3 -y
   
   # SYN flood simulation (use carefully!)
   sudo hping3 -S -p 80 --flood --rand-source <target-ip>
   ```

4. **Monitor Results**
   - Watch terminal output for detections
   - Check generated log file: `detection_log_*.json`
   - Blocked IPs are automatically filtered

5. **Stop the System**
   ```bash
   # Press Ctrl+C in the detection system terminal
   # It will save logs and show summary
   ```

### Key Features

- **Real-time Processing**: Analyzes packets as they arrive
- **Flow-based Analysis**: Groups packets into flows
- **ML Classification**: Uses trained model or heuristics
- **Automatic Blocking**: Blocks malicious IPs via XDP/iptables
- **Logging**: JSON logs for all detections

### Output Files

- `detection_log_YYYYMMDD_HHMMSS.json`: Detection logs
- Screenshots of terminal output
- Statistics summary

---

## Task 3: Frontend Interface

### Overview

Web-based dashboard for real-time monitoring of DDoS detections.

### Features

- 📊 **Live Statistics**: Total packets, malicious flows, blocked IPs
- 📋 **Detection Table**: Real-time log of all detected attacks
- 🎨 **Modern UI**: Glassmorphism design with animations
- 🔄 **Auto-refresh**: Updates every 2 seconds

### Running the Dashboard

1. **Start the Detection System** (if not already running)
   ```bash
   sudo python3 ddos_detection.py eth0
   ```

2. **In Another Terminal, Start Dashboard**
   ```bash
   python3 dashboard_app.py
   ```

3. **Access Dashboard**
   ```bash
   # Open in browser:
   http://localhost:5000
   
   # Or from Windows (if running in WSL):
   http://<WSL-IP>:5000
   
   # Find WSL IP:
   ip addr show eth0 | grep inet
   ```

4. **Dashboard Usage**
   - **Interface Selector**: Choose network interface (cosmetic)
   - **Clear Data**: Reset all statistics
   - **Refresh**: Reload the page
   - **Detection Table**: Shows all malicious traffic
   - **Statistics Cards**: Real-time metrics

### Screenshots Needed

1. Dashboard homepage with statistics
2. Detection table with multiple entries
3. Browser developer tools showing API calls
4. Mobile responsive view (optional)

### Customization

Edit `templates/dashboard.html` to customize:
- Colors and styling
- Refresh intervals
- Table columns
- Statistics cards

---

## Task 4: Containerization & Orchestration

### Overview

Deploy Docker containers for testing network communication and DDoS protection in isolated environments.

### Components

1. **Nginx Server**: Web server on port 8080
2. **Apache Server**: Web server on port 8081
3. **Test Client**: Ubuntu container for testing
4. **DDoS Detector**: (Optional) Containerized detection system

### Setup

1. **Install Docker** (if not already installed)
   ```bash
   # Install Docker on WSL
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   
   # Add user to docker group
   sudo usermod -aG docker $USER
   
   # Start Docker service
   sudo service docker start
   
   # Install Docker Compose
   sudo apt install docker-compose -y
   ```

2. **Verify Docker**
   ```bash
   docker --version
   docker-compose --version
   ```

3. **Run Testing Script**
   ```bash
   # This will:
   # - Create web content
   # - Start all containers
   # - Run connectivity tests
   # - Show results
   
   ./test_docker.sh
   ```

### Manual Container Operations

```bash
# Start containers
docker-compose up -d

# View running containers
docker-compose ps

# View logs
docker-compose logs -f

# Access test client
docker exec -it test_client_ddos_lab bash

# Inside test client, run:
ping nginx-server
ping apache-server
curl http://nginx-server
curl http://apache-server

# Stop containers
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Testing Communication

**From Test Client Container**:
```bash
# Get shell access
docker exec -it test_client_ddos_lab bash

# Inside the container:

# Test 1: Ping servers
ping -c 5 nginx-server
ping -c 5 apache-server

# Test 2: HTTP requests
curl http://nginx-server
curl http://apache-server

# Test 3: Trace route
traceroute nginx-server

# Test 4: Check network
ip addr
ip route
netstat -rn
```

**From Host (Windows/WSL)**:
```bash
# Access servers via browser:
# Nginx:  http://localhost:8080
# Apache: http://localhost:8081

# Or via curl:
curl http://localhost:8080
curl http://localhost:8081
```

### Docker Network Analysis

```bash
# Inspect network
docker network ls
docker network inspect lab4-ddos-defense_lab_network

# Get container IPs
docker inspect nginx_ddos_lab | grep IPAddress
docker inspect apache_ddos_lab | grep IPAddress

# View container details
docker inspect nginx_ddos_lab
```

### Screenshots Needed

1. `docker-compose ps` output
2. Successful ping to both servers
3. Curl output from both servers
4. Browser showing Nginx page (localhost:8080)
5. Browser showing Apache page (localhost:8081)
6. Network inspection commands
7. Docker network diagram (can create with draw.io)

---

## Running the Complete System

### Integrated Testing Scenario

**Terminal 1 - Detection System**:
```bash
sudo python3 ddos_detection.py eth0
```

**Terminal 2 - Dashboard**:
```bash
python3 dashboard_app.py
```

**Terminal 3 - Docker Containers**:
```bash
./test_docker.sh
docker exec -it test_client_ddos_lab bash
```

**Terminal 4 - Traffic Generation**:
```bash
# Generate normal traffic
ping 8.8.8.8

# Generate suspicious traffic
sudo hping3 -S --flood --rand-source localhost
```

**Browser**:
- Open http://localhost:5000 (Dashboard)
- Open http://localhost:8080 (Nginx)
- Open http://localhost:8081 (Apache)

---

## Troubleshooting

### XDP Issues

**Problem**: "Operation not supported" when loading XDP
```bash
# Solution: Use iptables fallback (already implemented)
# Verify iptables is working:
sudo iptables -L -n

# Our system automatically falls back to iptables
```

**Problem**: "Cannot find xdp-filter"
```bash
# Solution: Re-run setup
cd ~/xdp-tools
sudo make install
sudo ldconfig
```

### Python Issues

**Problem**: "Permission denied" when running detection
```bash
# Solution: Must run as root for packet capture
sudo python3 ddos_detection.py eth0
```

**Problem**: "No module named 'scapy'"
```bash
# Solution: Install dependencies
pip3 install -r requirements.txt

# Or install individually:
pip3 install scapy numpy flask
```

### Docker Issues

**Problem**: "Cannot connect to Docker daemon"
```bash
# Solution: Start Docker service
sudo service docker start

# Check status:
sudo service docker status
```

**Problem**: "Port already in use"
```bash
# Solution: Stop conflicting services
sudo lsof -i :8080
sudo lsof -i :8081

# Or change ports in docker-compose.yml
```

### WSL-Specific Issues

**Problem**: Cannot access dashboard from Windows browser
```bash
# Solution: Find WSL IP address
ip addr show eth0 | grep inet

# Use: http://<WSL-IP>:5000
# Example: http://172.20.10.5:5000
```

**Problem**: Network interface not found
```bash
# Solution: List available interfaces
ip link show

# Use the correct interface name in commands
```

---

## Report Guidelines

### Report Structure

**Title Page**:
- Lab 4: DDoS Defense (eBPF/XDP)
- Group Number: GX
- Student Names and Matriculation IDs
- Date

**Section 1: Introduction** (1 page)
- Brief overview of lab objectives
- System architecture diagram
- Tools and technologies used

**Section 2: Task 1 - XDP Configuration** (3-4 pages)
- Installation process
- Configuration steps
- Command outputs with screenshots
- WSL-specific challenges and solutions
- Comparison: XDP vs iptables

**Section 3: Task 2 - Real-Time Detection** (4-5 pages)
- System architecture and workflow
- FlowMeter implementation details
- ML Classifier (if used) or heuristic rules
- XDP/iptables integration
- Test scenarios and results
- Performance metrics

**Section 4: Task 3 - Frontend Interface** (2-3 pages)
- Dashboard architecture
- Features and functionality
- Screenshots of dashboard in action
- API design
- Real-time update mechanism

**Section 5: Task 4 - Containerization** (2-3 pages)
- Docker setup and configuration
- Container architecture diagram
- Communication tests with results
- Network analysis
- Security considerations

**Section 6: Results and Analysis** (2-3 pages)
- Complete system demonstration
- Performance evaluation
- Detection accuracy
- Response time metrics
- Limitations and challenges on WSL

**Section 7: Conclusion** (1 page)
- Summary of achievements
- Lessons learned
- Future improvements
- WSL vs VM comparison

**Appendices**:
- Complete code listings (if not on GitHub)
- Configuration files
- Additional screenshots
- Error logs and solutions

### Screenshots Checklist

#### Task 1
- [ ] xdp-filter help output
- [ ] XDP load command
- [ ] XDP status showing loaded program
- [ ] IP blocking command
- [ ] Port blocking command
- [ ] XDP statistics (poll)
- [ ] XDP unload

#### Task 2
- [ ] Detection system startup
- [ ] Flow statistics output
- [ ] Malicious traffic detection
- [ ] IP blocking action
- [ ] Detection log file contents
- [ ] Summary statistics

#### Task 3
- [ ] Dashboard home page
- [ ] Statistics cards with data
- [ ] Detection table with entries
- [ ] Browser DevTools network tab
- [ ] API response examples

#### Task 4
- [ ] docker-compose ps output
- [ ] Container network diagram
- [ ] Ping results (both servers)
- [ ] Curl outputs
- [ ] Nginx in browser
- [ ] Apache in browser
- [ ] Docker network inspect

### Code Submission

**GitHub Repository Structure**:
```
lab4-ddos-defense/
├── README.md
├── requirements.txt
├── setup_xdp_wsl.sh
├── test_xdp_filter.sh
├── ddos_detection.py
├── dashboard_app.py
├── docker-compose.yml
├── Dockerfile.detector
├── test_docker.sh
├── templates/
│   └── dashboard.html
├── logs/ (in .gitignore)
└── screenshots/
    ├── task1/
    ├── task2/
    ├── task3/
    └── task4/
```

**Requirements**:
1. Upload to GitHub with clear README
2. Include all source code
3. Add setup instructions
4. Document dependencies
5. Include .gitignore for logs
6. Share repository link in email

---

## Submission Checklist

- [ ] Report in PDF format: `GX.Report4.pdf`
- [ ] 15-20 pages (including screenshots)
- [ ] All four tasks completed
- [ ] GitHub repository created and shared
- [ ] Code is well-commented
- [ ] Requirements.txt included
- [ ] README with setup instructions
- [ ] Email sent to tf@sec.uni-passau.de
- [ ] Deadline: December 3, 2024

---

## Useful Commands Reference

### Network Analysis
```bash
# Show interfaces
ip link show
ip addr show

# Monitor traffic
sudo tcpdump -i eth0
sudo tcpdump -i eth0 -w capture.pcap

# Network statistics
netstat -i
netstat -s
ss -tuln
```

### Process Management
```bash
# Find Python processes
ps aux | grep python

# Kill process
sudo pkill -f ddos_detection

# Monitor resources
htop
iotop
```

### Log Analysis
```bash
# View logs
tail -f detection_log_*.json
cat detection_log_*.json | jq '.'

# Count detections
cat detection_log_*.json | jq 'length'

# Filter by IP
cat detection_log_*.json | jq '.[] | select(.src_ip=="10.46.0.1")'
```

---

## Credits

**Course**: Security Insider
**Lab**: 4 - DDoS Defense (eBPF/XDP)
**Instructor**: Talaya Farasat (tf@sec.uni-passau.de)
**Institution**: Passau Institute of Digital Security, University of Passau

---

## License

This project is for educational purposes only as part of the Security Insider course at the University of Passau.

---

## Support

For questions and issues:
- Email: tf@sec.uni-passau.de
- Office Hours: [Check StudIP]
- StudIP Forum: [Link]

**Good luck with your lab! 🚀**
