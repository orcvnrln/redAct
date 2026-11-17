@echo off
REM VibeShield Desktop - Ana Baslatma Skripti
REM Bu fayl layihe root-dadır, Desktop app-i baslatiir

title VibeShield Desktop
color 0A

echo.
echo ========================================
echo   VibeShield Desktop - DevSecOps Panel
echo ========================================
echo.

REM Check Python
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    color 0C
    echo [XETA] Python tapilmadi!
    echo.
    echo Python qurasdir: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo [OK] Python tapildi
python --version

REM Check desktop_app folder
if not exist "desktop_app\main.py" (
    color 0C
    echo [XETA] desktop_app\main.py tapilmadi!
    echo.
    echo Bu .bat faylini layihe root-dan isledir
    echo.
    pause
    exit /b 1
)

echo [OK] Desktop app tapildi
echo.
echo Desktop UI baslayir...
echo.
echo Pencere acilacaq. Bu terminali baglamayin!
echo.

REM Start desktop app
cd desktop_app
start "" python main.py

REM Wait a bit
timeout /t 2 >nul

echo.
echo ========================================
echo   Desktop UI baslatildi!
echo ========================================
echo.
echo Eger pencere acilmadisa:
echo   1. cd desktop_app
echo   2. python main.py
echo.
echo Bu terminali baglayin (X).
echo.
pause
