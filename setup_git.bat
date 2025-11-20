@echo off
REM Windows Batch Script to Setup Git Repository
REM Save this as: setup_git.bat
REM Run from your lab4-ddos-defense folder on Windows

echo ============================================
echo Lab 4 - Git Repository Setup (Windows)
echo ============================================
echo.

REM Check if Git is installed
where git >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Git is not installed or not in your PATH!
    echo.
    echo Please install Git from: https://git-scm.com/download/win
    echo Or use GitHub Desktop: https://desktop.github.com/
    pause
    exit /b 1
)

echo Git found: OK
echo.

REM Check if we're in a folder with files
if not exist "README.md" (
    echo ****************************************************
    echo ** ERROR: README.md not found! SCRIPT HALTED. **
    echo ****************************************************
    echo.
    echo Please make sure you're in the correct folder with all downloaded files.
    echo Current directory: %CD%
    pause
    exit /b 1
)

echo Files detected: OK
echo.

REM Initialize Git repository
echo [1/5] Initializing Git repository...
git init
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to initialize Git repository
    pause
    exit /b 1
)
echo      Done!
echo.

REM Add all files
echo [2/5] Adding all files...
git add .
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to add files
    pause
    exit /b 1
)
echo      Done!
echo.

REM Commit files
echo [3/5] Creating initial commit...
git commit -m "Lab 4: DDoS Defense System - Initial commit"
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to commit. (Are there files to commit?)
    pause
    exit /b 1
)
echo      Done!
echo.

REM Set main branch
echo [4/5] Setting branch name to 'main'...
git branch -M main
echo      Done!
echo.

REM Get GitHub username and repository name
echo [5/5] Adding remote repository...
echo.
echo Please enter your GitHub username:
set /p GITHUB_USER=Username: 

echo.
echo Enter repository name (default: lab4-ddos-defense):
set /p REPO_NAME=Repository name (press Enter for default): 

if "%REPO_NAME%"=="" set REPO_NAME=lab4-ddos-defense

echo.
echo Repository URL will be: https://github.com/%GITHUB_USER%/%REPO_NAME%.git
echo.
echo IMPORTANT: Make sure you've created this repository on GitHub first!
echo Go to: https://github.com/new
echo.
pause

REM Add remote
echo Attempting to add remote 'origin'...
git remote add origin https://github.com/%GITHUB_USER%/%REPO_NAME%.git
if %ERRORLEVEL% NEQ 0 (
    echo WARNING: Failed to add remote. This usually means 'origin' already exists.
    echo Trying to set URL instead...
    git remote set-url origin https://github.com/%GITHUB_USER%/%REPO_NAME%.git
    if %ERRORLEVEL% NEQ 0 (
        echo FATAL ERROR: Could not add or set remote URL.
        pause
        exit /b 1
    )
)
echo      Remote 'origin' successfully configured.
echo.

echo ============================================
echo Ready to push!
echo ============================================
echo.
echo To push your code to GitHub, run:
echo      git push -u origin main
echo.
echo You'll need to enter your GitHub credentials:
echo    - Username: %GITHUB_USER%
echo    - Password: Use a Personal Access Token (PAT)
echo.
echo To create a token:
echo    1. Go to: https://github.com/settings/tokens
echo    2. Generate new token (classic)
echo    3. Select 'repo' scope
echo    4. Copy the token and use it as password
echo.
echo After pushing, you can clone in WSL:
echo      git clone https://github.com/%GITHUB_USER%/%REPO_NAME%.git
echo.
pause

REM Optional: Ask if user wants to push now
echo.
echo Do you want to push to GitHub now? (y/n)
set /p PUSH_NOW=Push now?: 

if /i "%PUSH_NOW%"=="y" (
    echo.
    echo Pushing to GitHub...
    git push -u origin main
    if %ERRORLEVEL% EQU 0 (
        echo.
        echo ============================================
        echo SUCCESS! Repository pushed to GitHub!
        echo ============================================
        echo.
        echo Now clone it in WSL (if needed):
        echo      cd ~
        echo      git clone https://github.com/%GITHUB_USER%/%REPO_NAME%.git
        echo      cd %REPO_NAME%
        echo      chmod +x *.sh
        echo      ./quick_start.sh
    ) else (
        echo.
        echo Push failed. You can try again later with:
        echo      git push -u origin main
    )
)

echo.
echo ============================================
echo Setup complete!
echo ============================================
pause