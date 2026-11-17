@echo off
title VibeShield Modern UI
color 0B

echo.
echo ==========================================
echo   VibeShield - Modern Dashboard
echo ==========================================
echo.
echo Modern user-friendly interfeys acilir...
echo.

cd desktop_app
start "" python main_modern.py

timeout /t 2 >nul

echo.
echo [OK] Modern UI baslatildi!
echo.
echo Bu terminali baglaya bilersiniz.
echo.
pause
