@echo off
echo ============================================
echo   Push to GitHub with Token
echo ============================================
echo.

REM Check git
where git >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Git not installed!
    echo.
    echo Install Git first:
    echo   https://git-scm.com/download/win
    echo.
    echo After install, run this script again.
    pause
    exit /b 1
)

echo Git found! Proceeding...
echo.

REM Set credentials
set TOKEN=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
set REPO=https://github.com/orcvnrln/redAct.git

echo [1/7] Initializing repository...
git init
if %ERRORLEVEL% NEQ 0 goto :error

echo [2/7] Configuring Git...
git config user.email "vibeshield@example.com"
git config user.name "VibeShield"

echo [3/7] Adding files...
git add .
if %ERRORLEVEL% NEQ 0 goto :error

echo [4/7] Creating commit...
git commit -m "Initial commit: VibeShield Security Suite with Ontology UI"
if %ERRORLEVEL% NEQ 0 (
    echo No changes to commit or already committed
)

echo [5/7] Setting main branch...
git branch -M main

echo [6/7] Adding remote...
git remote remove origin 2>nul
git remote add origin %REPO%

echo [7/7] Pushing to GitHub...
echo.
git push --set-upstream https://orcvnrln:%TOKEN%@github.com/orcvnrln/redAct.git main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================
    echo   SUCCESS! Pushed to GitHub
    echo ============================================
    echo.
    echo View at: https://github.com/orcvnrln/redAct
    echo.
    echo Next steps:
    echo   1. Add OPENROUTER_API_KEY secret
    echo   2. Enable GitHub Actions
    echo.
) else (
    goto :error
)

pause
exit /b 0

:error
echo.
echo ============================================
echo   ERROR occurred
echo ============================================
echo.
pause
exit /b 1
