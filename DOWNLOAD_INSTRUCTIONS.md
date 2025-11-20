# 📥 DOWNLOAD INSTRUCTIONS - Start Here!

## Your Situation
- 🖥️ You're on Windows (chatting with Claude)
- 🐧 You need files in WSL
- ✅ Solution: Download → GitHub → Clone to WSL

---

## 🎯 Quick 3-Step Process

### Step 1: Download All Files (Windows) - 5 minutes

**Download these 18 files from Claude:**

Click on the outputs folder link and download each file:

#### Core Files (Must Download!)
1. ✅ setup_xdp_wsl.sh
2. ✅ test_xdp_filter.sh
3. ✅ test_docker.sh
4. ✅ quick_start.sh
5. ✅ check_submission.sh
6. ✅ verify_files.sh
7. ✅ ddos_detection.py
8. ✅ dashboard_app.py
9. ✅ traffic_generator.py
10. ✅ requirements.txt
11. ✅ docker-compose.yml
12. ✅ Dockerfile.detector
13. ✅ .gitignore
14. ✅ README.md
15. ✅ GETTING_STARTED.md
16. ✅ FILE_LIST.md
17. ✅ PROJECT_SUMMARY.md
18. ✅ GITHUB_SETUP_GUIDE.md
19. ✅ setup_git.bat (Windows helper script)
20. ✅ templates/dashboard.html (need to create templates folder!)

**Where to save:**
- Create folder: `C:\Users\YourName\lab4-ddos-defense`
- Save all files there
- Create subfolder: `templates`
- Put `dashboard.html` in the `templates` folder

### Step 2: Upload to GitHub (Windows) - 5 minutes

**Option A: Using the .bat script (Easiest!)**
```batch
1. Double-click setup_git.bat
2. Follow the prompts
3. Enter your GitHub username
4. Done!
```

**Option B: Manual commands**
```bash
# Open PowerShell/Command Prompt in your folder
cd C:\Users\YourName\lab4-ddos-defense

# Run these commands:
git init
git add .
git commit -m "Lab 4: Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/lab4-ddos-defense.git
git push -u origin main
```

**IMPORTANT:** 
- Create the repository on GitHub FIRST: https://github.com/new
- Name it: `lab4-ddos-defense`
- Make it: **PRIVATE** ⚠️

### Step 3: Clone in WSL (Linux) - 2 minutes

```bash
# Open WSL terminal
cd ~

# Clone your repository
git clone https://github.com/YOUR_USERNAME/lab4-ddos-defense.git

# Go to folder
cd lab4-ddos-defense

# Make scripts executable (IMPORTANT!)
chmod +x *.sh

# Verify everything
./verify_files.sh

# Start working
./quick_start.sh
```

---

## 📋 Detailed Instructions

### For Windows Users:

1. **Download all files from Claude** 
   - Right-click each file link → Save as
   - Or click to view → Ctrl+S to save
   - Save to: `C:\Users\YourName\lab4-ddos-defense`

2. **Install Git for Windows (if not installed)**
   - Download: https://git-scm.com/download/win
   - Or use GitHub Desktop: https://desktop.github.com/
   
3. **Create GitHub account (if don't have one)**
   - Go to: https://github.com/join
   - Free account is fine

4. **Create private repository**
   - Go to: https://github.com/new
   - Repository name: `lab4-ddos-defense`
   - Visibility: **Private** (important!)
   - Don't add README (we have our own)
   - Click "Create repository"

5. **Upload files using setup_git.bat**
   - Navigate to your folder with files
   - Double-click `setup_git.bat`
   - Follow the prompts
   - Enter credentials when asked

6. **Verify on GitHub**
   - Go to: https://github.com/YOUR_USERNAME/lab4-ddos-defense
   - Should see all your files!

### For WSL Users:

1. **Open WSL terminal** (Ubuntu)
   - Windows Start → Type "WSL" or "Ubuntu"
   - Or Windows Terminal → Ubuntu

2. **Install Git (if not installed)**
   ```bash
   sudo apt update
   sudo apt install git -y
   ```

3. **Clone repository**
   ```bash
   cd ~
   git clone https://github.com/YOUR_USERNAME/lab4-ddos-defense.git
   ```

4. **Configure permissions**
   ```bash
   cd lab4-ddos-defense
   chmod +x *.sh
   ```

5. **Verify and start**
   ```bash
   ./verify_files.sh
   ./quick_start.sh
   ```

---

## 🆘 Troubleshooting

### "I can't find the download button!"

**Solution:**
- You're chatting with Claude on Claude.ai
- I've put all files in a special outputs folder
- Look for links that say `computer:///mnt/user-data/outputs/filename`
- Click them to download

### "Git asks for password but it doesn't work!"

**Solution:**
- GitHub no longer accepts passwords
- You need a Personal Access Token:
  1. Go to: https://github.com/settings/tokens
  2. Click "Generate new token (classic)"
  3. Give it a name: "Lab4"
  4. Select scope: `repo` (check the box)
  5. Click "Generate token"
  6. **COPY THE TOKEN** (you won't see it again!)
  7. Use this token as your password when pushing

### "Files are there but scripts won't run!"

**Solution:**
```bash
# You forgot to make them executable!
chmod +x *.sh

# Now try again
./quick_start.sh
```

### "Can't clone - authentication failed!"

**Solution:**
```bash
# Make sure repository is created on GitHub first
# Check the URL is correct
# For private repos, you need authentication

# Use HTTPS with token:
git clone https://YOUR_TOKEN@github.com/YOUR_USERNAME/lab4-ddos-defense.git

# Or setup SSH keys (advanced)
```

---

## 📊 File Checklist

Before moving to WSL, verify you have:

**Scripts (6 files):**
- [ ] setup_xdp_wsl.sh
- [ ] test_xdp_filter.sh
- [ ] test_docker.sh
- [ ] quick_start.sh
- [ ] check_submission.sh
- [ ] verify_files.sh

**Python (3 files):**
- [ ] ddos_detection.py
- [ ] dashboard_app.py
- [ ] traffic_generator.py

**Config (4 files):**
- [ ] requirements.txt
- [ ] docker-compose.yml
- [ ] Dockerfile.detector
- [ ] .gitignore

**Docs (5 files):**
- [ ] README.md
- [ ] GETTING_STARTED.md
- [ ] FILE_LIST.md
- [ ] PROJECT_SUMMARY.md
- [ ] GITHUB_SETUP_GUIDE.md

**Web (1 folder + 1 file):**
- [ ] templates/
- [ ] templates/dashboard.html

**Windows Helper:**
- [ ] setup_git.bat

**Total: 20 items**

---

## ⚡ Ultra-Quick Version (For Experts)

```bash
# Windows (PowerShell):
cd C:\Users\YourName\lab4-ddos-defense
git init && git add . && git commit -m "Lab 4"
git remote add origin https://github.com/USER/lab4-ddos-defense.git
git push -u origin main

# WSL (Terminal):
cd ~ && git clone https://github.com/USER/lab4-ddos-defense.git
cd lab4-ddos-defense && chmod +x *.sh && ./quick_start.sh
```

---

## 🎓 Why GitHub?

**Benefits:**
- ✅ Easy transfer Windows → WSL
- ✅ Backup your work
- ✅ Version control
- ✅ Can share link with instructor
- ✅ Professional workflow
- ✅ Can work from any computer

**Remember:**
- Keep repository **PRIVATE**
- Don't share publicly (academic integrity)
- Can grant instructor access if needed

---

## 🎉 You're Ready!

Once files are in WSL:
1. ✅ Read `README.md` for complete guide
2. ✅ Run `./quick_start.sh` to begin
3. ✅ Follow task instructions
4. ✅ Take screenshots
5. ✅ Complete report
6. ✅ Submit with GitHub link

**Good luck! 🚀**

---

## 📧 For Your Submission

Include in your email to tf@sec.uni-passau.de:

```
GitHub Repository: https://github.com/YOUR_USERNAME/lab4-ddos-defense

Note: Repository is private. Please let me know if you need access.
```

This shows professionalism and makes it easy for the instructor to review your code!
