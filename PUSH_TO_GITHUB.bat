@echo off
echo ============================================
echo   Git Setup for VibeShield
echo ============================================
echo.

REM Check if git is installed
where git >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Git is not installed!
    echo.
    echo Please install Git first:
    echo   1. Download: https://git-scm.com/download/win
    echo   2. Install with default settings
    echo   3. Restart this terminal
    echo   4. Run this script again
    echo.
    pause
    exit /b 1
)

echo Git found! Continuing...
echo.

REM Initialize repo
echo [1/6] Initializing Git repository...
git init
if %ERRORLEVEL% NEQ 0 goto :error

REM Add all files
echo [2/6] Adding all files...
git add .
if %ERRORLEVEL% NEQ 0 goto :error

REM First commit
echo [3/6] Creating first commit...
git commit -m "Initial commit: VibeShield Security Suite with Ontology UI"
if %ERRORLEVEL% NEQ 0 goto :error

REM Set main branch
echo [4/6] Setting main branch...
git branch -M main
if %ERRORLEVEL% NEQ 0 goto :error

REM Add remote
echo [5/6] Adding GitHub remote...
git remote remove origin 2>nul
git remote add origin https://github.com/orcvnrln/redAct.git
if %ERRORLEVEL% NEQ 0 goto :error

REM Push
echo [6/6] Pushing to GitHub...
echo.
echo You may be asked for GitHub credentials:
echo   Username: orcvnrln
echo   Password: Use Personal Access Token (not your password!)
echo.
echo To create token: https://github.com/settings/tokens
echo   - Select: repo, workflow permissions
echo   - Copy and use as password
echo.
git push -u origin main
if %ERRORLEVEL% NEQ 0 goto :error

echo.
echo ============================================
echo   SUCCESS! Repository pushed to GitHub
echo ============================================
echo.
echo View your repo at:
echo   https://github.com/orcvnrln/redAct
echo.
echo Next steps:
echo   1. Add OPENROUTER_API_KEY secret in GitHub
echo   2. Enable GitHub Actions
echo   3. Push again to trigger pipeline
echo.
pause
exit /b 0

:error
echo.
echo ============================================
echo   ERROR: Git operation failed
echo ============================================
echo.
echo Common issues:
echo   1. Authentication failed - use Personal Access Token
echo   2. Remote already exists - script handles this
echo   3. No changes to commit - already done
echo.
pause
exit /b 1
