# 📁 Lab 4 Project Files - Complete List

## 📋 File Structure Overview

```
lab4-ddos-defense/
├── Core Application Files
│   ├── ddos_detection.py          (Main detection system)
│   ├── dashboard_app.py            (Web dashboard backend)
│   └── traffic_generator.py        (Traffic simulation tool)
│
├── Setup & Testing Scripts
│   ├── setup_xdp_wsl.sh           (XDP installation)
│   ├── test_xdp_filter.sh         (XDP testing)
│   ├── test_docker.sh             (Docker testing)
│   ├── quick_start.sh             (Quick setup)
│   └── check_submission.sh        (Submission checker)
│
├── Docker Configuration
│   ├── docker-compose.yml         (Container orchestration)
│   └── Dockerfile.detector        (Detector image)
│
├── Web Interface
│   └── templates/
│       └── dashboard.html         (Dashboard UI)
│
├── Documentation
│   ├── README.md                  (Complete guide)
│   ├── GETTING_STARTED.md         (Quick start)
│   └── FILE_LIST.md               (This file)
│
├── Configuration
│   ├── requirements.txt           (Python dependencies)
│   └── .gitignore                 (Git ignore rules)
│
└── Generated at Runtime
    ├── logs/                      (Detection logs)
    ├── screenshots/               (Task screenshots)
    └── detection_log_*.json       (Detection data)
```

---

## 🎯 File Descriptions

### Core Application Files

#### `ddos_detection.py` (⭐ MAIN FILE - Task 2)
**Purpose:** Real-time DDoS detection and mitigation system

**Features:**
- Packet capture using Scapy
- Flow-based traffic analysis
- ML classification (or heuristic detection)
- Automatic IP blocking via XDP/iptables
- JSON logging of all detections

**Usage:**
```bash
sudo python3 ddos_detection.py eth0 [model.pkl]
```

**Requirements:**
- Root privileges (for packet capture)
- Network interface name
- Optional: pre-trained ML model from Lab 2/3

**Output:**
- Terminal: Real-time detection alerts
- File: `detection_log_YYYYMMDD_HHMMSS.json`
- System: Blocked IPs via iptables/XDP

---

#### `dashboard_app.py` (⭐ MAIN FILE - Task 3)
**Purpose:** Web-based monitoring dashboard

**Features:**
- Flask web server
- RESTful API for detection data
- Real-time statistics
- Auto-refresh every 2 seconds
- Responsive design

**Usage:**
```bash
python3 dashboard_app.py
# Then open: http://localhost:5000
```

**API Endpoints:**
- `GET /` - Dashboard homepage
- `GET /api/detections` - Get all detections
- `GET /api/stats` - Get statistics
- `POST /api/add_detection` - Add detection (testing)
- `GET /api/clear` - Clear all data

**Technologies:**
- Backend: Flask + Flask-CORS
- Frontend: HTML5 + CSS3 + JavaScript
- Styling: Modern glassmorphism design

---

#### `traffic_generator.py` (🧪 TESTING TOOL)
**Purpose:** Generate traffic for testing detection system

**Features:**
- Multiple traffic patterns
- Configurable intensity and duration
- Both normal and malicious traffic
- Mixed scenario support

**Usage:**
```bash
# Normal traffic
sudo python3 traffic_generator.py -t 127.0.0.1 -m normal -d 60

# SYN flood attack
sudo python3 traffic_generator.py -t 127.0.0.1 -m syn_flood -d 30

# Mixed scenario (normal → attack → normal)
sudo python3 traffic_generator.py -t 127.0.0.1 -m mixed -d 60
```

**Traffic Modes:**
- `normal` - Legitimate HTTP-like traffic
- `syn_flood` - SYN flood DDoS attack
- `udp_flood` - UDP flood attack
- `icmp_flood` - ICMP ping flood
- `http_flood` - HTTP GET flood
- `mixed` - Combination of normal and attack

---

### Setup & Testing Scripts

#### `setup_xdp_wsl.sh` (⭐ SETUP - Task 1)
**Purpose:** Install and configure XDP tools on WSL

**What it does:**
1. Checks WSL environment
2. Installs dependencies (clang, llvm, libelf, etc.)
3. Builds and installs libbpf
4. Clones and builds xdp-tools
5. Verifies installation

**Usage:**
```bash
sudo ./setup_xdp_wsl.sh
```

**Duration:** 10-15 minutes
**Requirements:** Internet connection, 2GB free space

---

#### `test_xdp_filter.sh` (🧪 TESTING - Task 1)
**Purpose:** Test XDP filter functionality with examples

**What it tests:**
1. Load XDP filter on interface
2. Check status
3. Block specific IP addresses
4. Block specific ports
5. View statistics
6. Unload filter

**Usage:**
```bash
sudo ./test_xdp_filter.sh
# Or specify interface:
sudo ./test_xdp_filter.sh eth0
```

**Take screenshots of ALL outputs!**

---

#### `test_docker.sh` (🧪 TESTING - Task 4)
**Purpose:** Setup and test Docker container environment

**What it does:**
1. Creates sample web content
2. Starts Docker containers (Nginx, Apache, Test client)
3. Runs connectivity tests
4. Displays network information
5. Provides testing commands

**Usage:**
```bash
./test_docker.sh
```

**Services:**
- Nginx: http://localhost:8080
- Apache: http://localhost:8081
- Test client: For internal testing

---

#### `quick_start.sh` (🚀 QUICK SETUP)
**Purpose:** Fast initial setup and environment check

**What it does:**
1. Checks system requirements
2. Installs basic dependencies
3. Verifies Python packages
4. Creates directory structure
5. Provides next steps

**Usage:**
```bash
./quick_start.sh
```

**Perfect for:** First-time setup, getting started quickly

---

#### `check_submission.sh` (✅ FINAL CHECK)
**Purpose:** Verify submission readiness

**What it checks:**
1. Required files present
2. Screenshot directories and counts
3. Report existence and format
4. Code quality and syntax
5. Git repository status
6. Overall completion percentage

**Usage:**
```bash
./check_submission.sh
```

**Run before submission!**

---

### Docker Configuration

#### `docker-compose.yml` (🐳 DOCKER - Task 4)
**Purpose:** Define and orchestrate multiple containers

**Services:**
- `nginx-server` - Nginx web server (port 8080)
- `apache-server` - Apache web server (port 8081)
- `test-client` - Ubuntu testing container
- `ddos-detector` - Optional detector container

**Network:**
- Custom bridge network: `lab_network`
- Subnet: 172.20.0.0/16
- All containers can communicate

**Usage:**
```bash
docker-compose up -d        # Start all containers
docker-compose ps           # View status
docker-compose logs -f      # View logs
docker-compose down         # Stop all containers
```

---

#### `Dockerfile.detector` (🐳 DOCKER)
**Purpose:** Build containerized detection system

**Based on:** Ubuntu 22.04
**Includes:**
- Python 3 and dependencies
- XDP/eBPF tools
- Network utilities
- Detection scripts

**Usage:**
```bash
docker build -f Dockerfile.detector -t ddos-detector .
docker run --privileged ddos-detector
```

---

### Web Interface

#### `templates/dashboard.html` (🎨 FRONTEND - Task 3)
**Purpose:** Web dashboard user interface

**Features:**
- Modern glassmorphism design
- Real-time statistics cards
- Detection log table
- Auto-refresh functionality
- Responsive layout

**Technologies:**
- HTML5 semantic markup
- CSS3 animations and gradients
- Vanilla JavaScript (no frameworks)
- Fetch API for backend communication

**Styling:**
- Gradient background
- Glass-effect cards
- Smooth animations
- Mobile-responsive

---

### Documentation

#### `README.md` (📖 COMPLETE GUIDE)
**Purpose:** Comprehensive project documentation

**Sections:**
- Overview and architecture
- WSL-specific setup
- Detailed task instructions
- Troubleshooting guide
- Report requirements
- Submission checklist

**Length:** ~17,000 words
**Read time:** 30-45 minutes

---

#### `GETTING_STARTED.md` (⚡ QUICK GUIDE)
**Purpose:** Fast-track guide for quick setup

**Sections:**
- 5-minute setup
- Task summaries
- Quick test scenarios
- Screenshot checklist
- Troubleshooting quick fixes

**Length:** ~2,500 words
**Read time:** 10 minutes

---

### Configuration

#### `requirements.txt` (📦 DEPENDENCIES)
**Purpose:** Python package requirements

**Packages:**
- scapy==2.5.0 - Packet manipulation
- numpy==1.24.3 - Numerical computing
- scikit-learn==1.3.0 - Machine learning
- pandas==2.0.3 - Data analysis
- flask==3.0.0 - Web framework
- flask-cors==4.0.0 - CORS support
- matplotlib==3.7.2 - Plotting
- seaborn==0.12.2 - Visualization

**Installation:**
```bash
pip3 install -r requirements.txt
```

---

#### `.gitignore` (🚫 GIT IGNORE)
**Purpose:** Specify files to exclude from Git

**Ignores:**
- Python cache files
- Virtual environments
- Log files
- Temporary files
- Docker build artifacts
- IDE configurations

---

## 📊 File Size Summary

| File | Size | Language | Lines |
|------|------|----------|-------|
| ddos_detection.py | ~14 KB | Python | ~450 |
| dashboard_app.py | ~3.5 KB | Python | ~110 |
| traffic_generator.py | ~9.5 KB | Python | ~280 |
| dashboard.html | ~9 KB | HTML/CSS/JS | ~300 |
| README.md | ~17 KB | Markdown | ~650 |
| setup_xdp_wsl.sh | ~3 KB | Bash | ~100 |
| docker-compose.yml | ~2 KB | YAML | ~70 |

**Total Project Size:** ~60 KB (without dependencies)

---

## 🔄 File Dependencies

```
ddos_detection.py
├── Requires: scapy, numpy, scikit-learn
├── Depends on: requirements.txt
├── Creates: detection_log_*.json
└── Uses: XDP tools (if available)

dashboard_app.py
├── Requires: flask, flask-cors
├── Depends on: templates/dashboard.html
└── Reads: detection_log_*.json

traffic_generator.py
├── Requires: scapy
└── Creates: Network traffic

docker-compose.yml
├── Depends on: Dockerfile.detector
└── Creates: Docker containers

All scripts
└── Require: chmod +x (executable permission)
```

---

## 🎯 Which Files to Use for Each Task

### Task 1: XDP Configuration
**Primary:**
- `setup_xdp_wsl.sh`
- `test_xdp_filter.sh`

**Reference:**
- `README.md` (Task 1 section)

---

### Task 2: Real-Time Detection
**Primary:**
- `ddos_detection.py`
- `traffic_generator.py`

**Optional:**
- Model file from Lab 2/3 (`model.pkl`)

**Reference:**
- `README.md` (Task 2 section)

---

### Task 3: Frontend Interface
**Primary:**
- `dashboard_app.py`
- `templates/dashboard.html`

**Requires:**
- `ddos_detection.py` (running)

**Reference:**
- `README.md` (Task 3 section)

---

### Task 4: Containerization
**Primary:**
- `docker-compose.yml`
- `test_docker.sh`

**Optional:**
- `Dockerfile.detector`

**Reference:**
- `README.md` (Task 4 section)

---

## 📝 How to Use This Project

### First Time Setup:
```bash
1. ./quick_start.sh
2. Read README.md
3. sudo ./setup_xdp_wsl.sh
```

### Running Tests:
```bash
# Task 1
sudo ./test_xdp_filter.sh

# Task 2
sudo python3 ddos_detection.py eth0

# Task 3
python3 dashboard_app.py

# Task 4
./test_docker.sh
```

### Before Submission:
```bash
./check_submission.sh
```

---

## 🆘 If Something Goes Wrong

1. **Read error messages carefully**
2. **Check README.md troubleshooting section**
3. **Verify all dependencies installed**
4. **Ensure running as root (sudo) when needed**
5. **Check network interface name**
6. **Review logs in `logs/` directory**

---

## 📧 Support

**Email:** tf@sec.uni-passau.de
**Subject:** Lab 4 - [Brief description of issue]

**Include:**
- Error messages
- Commands you ran
- System information
- Screenshots if relevant

---

## ✅ Quick Checklist

Before starting, ensure you have:
- [ ] All files downloaded
- [ ] WSL2 with Ubuntu 22.04
- [ ] At least 4GB free space
- [ ] Internet connection
- [ ] Sudo/root access
- [ ] Text editor or IDE
- [ ] Screenshot tool ready

---

**Good luck with your lab! 🚀**

*Last updated: November 2024*
*Lab 4 - Security Insider*
*University of Passau*
