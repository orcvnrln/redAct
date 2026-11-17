@echo off
echo ============================================
echo   VibeShield Pro - UI Test
echo ============================================
echo.
echo Testing API Key Display Fix...
echo.
python test_settings.py
echo.
echo ============================================
echo   Launching UI...
echo ============================================
echo.
python vibeshield_pro.py
