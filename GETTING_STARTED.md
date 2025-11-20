# 🚀 QUICK START - Lab 4 DDoS Defense

**For WSL Users - Start Here!**

## ⚡ Fast Setup (5 minutes)

```bash
# 1. Download and extract all files
# 2. Open WSL/Ubuntu terminal
cd ~/
mkdir lab4-ddos-defense
cd lab4-ddos-defense
# Copy all downloaded files here

# 3. Run quick start
chmod +x quick_start.sh
./quick_start.sh
```

## 📝 What You'll Build

1. **XDP/eBPF Filter** - Kernel-level packet filtering
2. **DDoS Detector** - Real-time traffic analysis with ML
3. **Web Dashboard** - Beautiful monitoring interface
4. **Docker Environment** - Containerized testing setup

## 🎯 Tasks Overview

### Task 1: XDP Configuration (30 mins)
```bash
sudo ./setup_xdp_wsl.sh        # Install XDP tools
sudo ./test_xdp_filter.sh      # Test XDP filtering
```

**Take screenshots of:**
- Installation output
- XDP filter commands
- Blocking rules
- Statistics

### Task 2: Real-Time Detection (1 hour)
```bash
# Terminal 1: Start detector
sudo python3 ddos_detection.py eth0

# Terminal 2: Generate traffic
sudo python3 traffic_generator.py -t 127.0.0.1 -m mixed -d 60
```

**Take screenshots of:**
- Detection system running
- Traffic classifications
- Blocked IPs
- Log files

### Task 3: Web Dashboard (30 mins)
```bash
# Terminal 1: Keep detector running
sudo python3 ddos_detection.py eth0

# Terminal 2: Start dashboard
python3 dashboard_app.py

# Browser: http://localhost:5000
```

**Take screenshots of:**
- Dashboard with live data
- Statistics cards
- Detection table
- Different views

### Task 4: Docker Setup (30 mins)
```bash
./test_docker.sh

# Test communication
docker exec -it test_client_ddos_lab bash
ping nginx-server
curl http://nginx-server
```

**Take screenshots of:**
- Docker containers running
- Ping results
- Web pages in browser
- Network analysis

## 🔥 Quick Test Scenario

**Complete End-to-End Test (10 minutes):**

```bash
# Terminal 1: Detection
sudo python3 ddos_detection.py eth0

# Terminal 2: Dashboard
python3 dashboard_app.py

# Terminal 3: Docker
docker-compose up -d
docker exec -it test_client_ddos_lab bash

# Terminal 4: Traffic
sudo python3 traffic_generator.py -t 127.0.0.1 -m mixed -d 60

# Browser: 
# http://localhost:5000 (Dashboard)
# http://localhost:8080 (Nginx)
# http://localhost:8081 (Apache)
```

## 📸 Screenshot Checklist

### Task 1 (7 screenshots minimum)
- [ ] XDP help command
- [ ] XDP load on interface
- [ ] XDP status
- [ ] Blocking IP rule
- [ ] Blocking port rule
- [ ] Statistics output
- [ ] Any errors (document for WSL)

### Task 2 (6 screenshots minimum)
- [ ] Detection system start
- [ ] Normal traffic processing
- [ ] Malicious detection alert
- [ ] IP blocking action
- [ ] Detection log file
- [ ] Summary statistics

### Task 3 (5 screenshots minimum)
- [ ] Dashboard homepage
- [ ] Live statistics
- [ ] Detection table with data
- [ ] API responses in DevTools
- [ ] Mobile/responsive view

### Task 4 (7 screenshots minimum)
- [ ] docker-compose ps
- [ ] Ping to nginx
- [ ] Ping to apache
- [ ] Curl nginx response
- [ ] Curl apache response
- [ ] Browser nginx page
- [ ] Browser apache page

## 🛠️ Troubleshooting

**"XDP not supported"**
→ Normal on WSL! System falls back to iptables automatically.

**"Permission denied"**
→ Use `sudo` for network tools: `sudo python3 ddos_detection.py`

**"Can't find interface"**
→ Check available: `ip link show`, use correct name

**"Docker not working"**
→ Start service: `sudo service docker start`

**"Port already in use"**
→ Change ports in docker-compose.yml or kill conflicting process

## 📦 Files Included

### Core Files
- `ddos_detection.py` - Main detection system
- `dashboard_app.py` - Web dashboard
- `traffic_generator.py` - Traffic simulator
- `requirements.txt` - Python dependencies

### Setup Scripts
- `setup_xdp_wsl.sh` - Install XDP tools
- `test_xdp_filter.sh` - Test XDP functionality
- `test_docker.sh` - Setup Docker environment
- `quick_start.sh` - Quick setup guide

### Docker Files
- `docker-compose.yml` - Container orchestration
- `Dockerfile.detector` - Detector container

### Documentation
- `README.md` - Complete guide (READ THIS!)
- `GETTING_STARTED.md` - This file
- `.gitignore` - Git ignore rules

### Utilities
- `check_submission.sh` - Verify submission readiness

## 🎓 Report Requirements

**File:** `GX.Report4.pdf` (X = your group number)
**Length:** 15-20 pages
**Include:**
- All task screenshots
- Code explanations
- Results and analysis
- GitHub link
- WSL challenges and solutions

**Structure:**
1. Introduction (1 page)
2. Task 1: XDP (3-4 pages)
3. Task 2: Detection (4-5 pages)
4. Task 3: Dashboard (2-3 pages)
5. Task 4: Docker (2-3 pages)
6. Results (2-3 pages)
7. Conclusion (1 page)

## 📧 Submission

**Email:** tf@sec.uni-passau.de
**Subject:** Lab-2025: matriculation ID-1, matriculation ID-2
**Attach:** GX.Report4.pdf
**Include:** GitHub repository link
**Deadline:** December 3, 2024

**IMPORTANT:** Reply to same email thread from Lab 1!

## 🌟 Success Criteria

✅ All 4 tasks completed with screenshots
✅ Code runs without critical errors
✅ Report 15-20 pages with all sections
✅ GitHub repository with clean code
✅ Submission on time

## 💡 Pro Tips

1. **Start Early** - Don't wait until deadline
2. **Test Everything** - Run each component before moving on
3. **Screenshot Everything** - Take more than you need
4. **Document Errors** - WSL limitations are expected, just document them
5. **Clean Code** - Add comments, use meaningful variable names
6. **Git Often** - Commit frequently with clear messages

## 🆘 Need Help?

**Email:** tf@sec.uni-passau.de
**Documentation:** See README.md for detailed info
**Troubleshooting:** Check "Troubleshooting" section in README.md

---

## ⚡ TL;DR - Absolute Minimum to Pass

```bash
# 1. Setup (5 min)
./quick_start.sh

# 2. Task 1 (30 min)
sudo ./setup_xdp_wsl.sh
sudo ./test_xdp_filter.sh
# Take 7 screenshots

# 3. Task 2 (1 hour)
sudo python3 ddos_detection.py eth0
sudo python3 traffic_generator.py -t 127.0.0.1 -m mixed -d 60
# Take 6 screenshots

# 4. Task 3 (30 min)  
python3 dashboard_app.py
# Open http://localhost:5000
# Take 5 screenshots

# 5. Task 4 (30 min)
./test_docker.sh
# Take 7 screenshots

# 6. Report (3 hours)
# Write 15-20 pages with all screenshots

# 7. Submit
# Email report + GitHub link to tf@sec.uni-passau.de
```

**Total Time: ~6-8 hours**

Good luck! 🎉
