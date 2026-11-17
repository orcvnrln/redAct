@echo off
title VibeShield - Sadə UI
color 0A

echo.
echo ================================================
echo       VibeShield - Sadə Desktop UI
echo ================================================
echo.
echo Rahat ve aydin interfeys acilir...
echo.

cd desktop_app
start "" python vibeshield_ui.py

timeout /t 2 >nul

echo.
echo [OK] UI baslatildi!
echo.
echo Bu pencereni baglaya bilersiniz.
echo.
pause
