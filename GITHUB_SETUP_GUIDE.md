# 🚀 GitHub/GitLab Setup Guide - Windows to WSL

## Your Situation
- ✅ Chatting from Windows (Host)
- ✅ Need files in WSL (Subsystem)
- ✅ Best solution: GitHub/GitLab

---

## 📋 Method 1: GitHub (Recommended)

### Step 1: Download All Files (Windows)

1. Click this link to download all files: [Download outputs folder](computer:///mnt/user-data/outputs/)
2. Save all files to a folder like: `C:\Users\YourName\lab4-ddos-defense`

**Files to download (17 files):**
```
✓ setup_xdp_wsl.sh
✓ test_xdp_filter.sh
✓ test_docker.sh
✓ quick_start.sh
✓ check_submission.sh
✓ verify_files.sh
✓ ddos_detection.py
✓ dashboard_app.py
✓ traffic_generator.py
✓ requirements.txt
✓ docker-compose.yml
✓ Dockerfile.detector
✓ .gitignore
✓ README.md
✓ GETTING_STARTED.md
✓ FILE_LIST.md
✓ PROJECT_SUMMARY.md
✓ templates/dashboard.html (create templates folder first!)
```

### Step 2: Create GitHub Repository (Windows)

**Option A: Via GitHub Website** (Easiest)

1. Go to https://github.com/new
2. Repository name: `lab4-ddos-defense`
3. Description: "Security Insider Lab 4 - DDoS Defense using eBPF/XDP"
4. Choose: **Private** (recommended for coursework)
5. ✅ Check "Add a README file" (optional, we have our own)
6. ✅ Check "Add .gitignore" → Select "Python"
7. Click "Create repository"

**Option B: Via Git Command Line** (Windows)

```bash
# Open Command Prompt or PowerShell
cd C:\Users\YourName\lab4-ddos-defense

# Initialize Git
git init

# Add all files
git add .

# Make initial commit
git commit -m "Lab 4: Initial commit - DDoS Defense System"

# Add GitHub remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/lab4-ddos-defense.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### Step 3: Clone in WSL (Linux)

Open WSL terminal and run:

```bash
# Navigate to home directory
cd ~

# Clone your repository
git clone https://github.com/YOUR_USERNAME/lab4-ddos-defense.git

# Enter the directory
cd lab4-ddos-defense

# Verify all files are there
ls -la

# Make scripts executable
chmod +x *.sh

# Run verification
./verify_files.sh
```

**Done! You now have all files in WSL! 🎉**

---

## 📋 Method 2: GitLab (Alternative)

### Step 1: Create GitLab Repository

1. Go to https://gitlab.com/projects/new
2. Project name: `lab4-ddos-defense`
3. Visibility: **Private**
4. Initialize with README: No (we have our own)
5. Click "Create project"

### Step 2: Push from Windows

```bash
cd C:\Users\YourName\lab4-ddos-defense

git init
git add .
git commit -m "Lab 4: Initial commit"
git remote add origin https://gitlab.com/YOUR_USERNAME/lab4-ddos-defense.git
git branch -M main
git push -u origin main
```

### Step 3: Clone in WSL

```bash
cd ~
git clone https://gitlab.com/YOUR_USERNAME/lab4-ddos-defense.git
cd lab4-ddos-defense
chmod +x *.sh
```

---

## 📋 Method 3: Direct Windows → WSL Transfer (Quick Alternative)

If you don't want to use Git, you can directly copy:

### Option A: Using Windows File Explorer

1. Download all files to Windows folder
2. Open WSL terminal
3. Copy from Windows to WSL:

```bash
# In WSL terminal
cd ~
mkdir lab4-ddos-defense
cd lab4-ddos-defense

# Copy from Windows Downloads (adjust path for your username)
cp -r /mnt/c/Users/YourName/Downloads/lab4-files/* .

# Or copy from specific folder
cp -r /mnt/c/Users/YourName/lab4-ddos-defense/* .

# Make scripts executable
chmod +x *.sh
```

### Option B: Using WSL from Windows

1. In Windows File Explorer, navigate to: `\\wsl$\Ubuntu\home\your-linux-username\`
2. Create folder: `lab4-ddos-defense`
3. Copy all downloaded files there
4. Open WSL and run: `chmod +x ~/lab4-ddos-defense/*.sh`

---

## 🎯 Recommended Workflow (Best Practice)

Here's what I recommend:

```
┌─────────────────────────────────────────────────────┐
│ Windows (Host)                                      │
│                                                     │
│ 1. Download files from Claude                      │
│ 2. Create private GitHub repository                │
│ 3. Push all files to GitHub                        │
└─────────────────────┬───────────────────────────────┘
                      │
                      │ GitHub/GitLab
                      │ (Cloud Storage)
                      │
┌─────────────────────▼───────────────────────────────┐
│ WSL (Linux)                                         │
│                                                     │
│ 4. Clone repository from GitHub                    │
│ 5. chmod +x *.sh                                   │
│ 6. Start working on lab                            │
└─────────────────────────────────────────────────────┘
```

**Benefits of using Git:**
- ✅ Version control (track changes)
- ✅ Backup in cloud
- ✅ Easy to share with instructor
- ✅ Can include GitHub link in report
- ✅ Can update from anywhere
- ✅ Professional workflow

---

## 📝 Quick Commands Cheat Sheet

### On Windows (First time):
```bash
cd C:\Users\YourName\lab4-ddos-defense
git init
git add .
git commit -m "Lab 4: Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/lab4-ddos-defense.git
git push -u origin main
```

### On WSL (First time):
```bash
cd ~
git clone https://github.com/YOUR_USERNAME/lab4-ddos-defense.git
cd lab4-ddos-defense
chmod +x *.sh
./quick_start.sh
```

### Update files later (if you make changes):

**On Windows:**
```bash
git add .
git commit -m "Updated code"
git push
```

**On WSL:**
```bash
git pull
chmod +x *.sh
```

---

## 🔐 Important: Private Repository!

**⚠️ Make your repository PRIVATE because:**
- This is coursework
- Sharing solutions publicly = academic dishonesty
- Keep it private until after the course ends
- You can share the link privately with your instructor

---

## 🆘 Troubleshooting

### "git not found" on Windows

**Solution:**
```bash
# Download Git for Windows from:
https://git-scm.com/download/win

# Or use GitHub Desktop (easier):
https://desktop.github.com/
```

### "git not found" on WSL

**Solution:**
```bash
sudo apt update
sudo apt install git -y
```

### "Permission denied (publickey)" when pushing

**Solution:**

**Option A: Use HTTPS instead** (Easier)
```bash
git remote set-url origin https://github.com/YOUR_USERNAME/lab4-ddos-defense.git
# GitHub will ask for your username and password/token
```

**Option B: Setup SSH keys**
```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"

# Copy public key
cat ~/.ssh/id_ed25519.pub

# Add to GitHub: Settings → SSH and GPG keys → New SSH key
```

### "Authentication failed" on GitHub

**Solution:**
- GitHub no longer accepts passwords
- Create a Personal Access Token:
  1. GitHub → Settings → Developer settings → Personal access tokens
  2. Generate new token (classic)
  3. Select scopes: `repo`
  4. Use token as password when pushing

---

## 📦 Complete Setup Example

Here's a complete example from start to finish:

### On Windows:

```bash
# 1. Open PowerShell or Command Prompt
cd C:\Users\YourName\Downloads

# 2. Create project folder
mkdir lab4-ddos-defense
cd lab4-ddos-defense

# 3. Download all files from Claude to this folder
# (Click download links, save to this folder)

# 4. Verify files (should see 17 files)
dir

# 5. Initialize Git
git init

# 6. Add all files
git add .

# 7. Commit
git commit -m "Lab 4: DDoS Defense System - Initial commit"

# 8. Add remote (create repo on GitHub first!)
git remote add origin https://github.com/YOUR_USERNAME/lab4-ddos-defense.git

# 9. Push
git branch -M main
git push -u origin main
```

### On WSL:

```bash
# 1. Open WSL terminal
cd ~

# 2. Clone repository
git clone https://github.com/YOUR_USERNAME/lab4-ddos-defense.git

# 3. Enter directory
cd lab4-ddos-defense

# 4. List files (should see all 17 files)
ls -la

# 5. Make scripts executable
chmod +x *.sh

# 6. Verify everything is ready
./verify_files.sh

# 7. Start setup
./quick_start.sh

# 8. Success! Start working on labs
```

---

## 🎓 For Your Report

Include in your report:

```
Repository: https://github.com/YOUR_USERNAME/lab4-ddos-defense

Note: Repository is currently private for academic integrity.
Access can be granted upon request.
```

---

## ✅ Final Checklist

Before starting the lab, make sure:

- [ ] All 17 files downloaded on Windows
- [ ] GitHub/GitLab repository created (PRIVATE)
- [ ] Files pushed to GitHub/GitLab
- [ ] Repository cloned in WSL
- [ ] Scripts are executable (`chmod +x *.sh`)
- [ ] Verification script confirms all files present
- [ ] Ready to run `./quick_start.sh`

---

## 🎉 You're All Set!

Once files are in WSL, you can:
1. Run `./quick_start.sh` to start
2. Follow README.md for detailed instructions
3. Complete all 4 tasks
4. Take screenshots
5. Write your report
6. Include GitHub link in submission

**Good luck! 🚀**
