@echo off
title VibeShield Desktop - DevSecOps Panel
cd /d "%~dp0"

REM Python yoxla
python --version >nul 2>&1
if errorlevel 1 (
    echo [XETA] Python tapilmadi!
    echo Python qurasdir: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Asililiklar yoxla
python -c "import tkinter" >nul 2>&1
if errorlevel 1 (
    echo [XETA] Tkinter tapilmadi!
    echo Python-u tkinter ile yeniden qurasdir
    pause
    exit /b 1
)

echo VibeShield Desktop baslatilir...
python main.py

if errorlevel 1 (
    echo.
    echo [XETA] Proqram xeta ile baglandı
    pause
)
