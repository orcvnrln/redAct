@echo off
rem VibeShield Desktop başlat — Windows
rem   start_desktop.bat              ^> GUI
rem   start_desktop.bat --selftest   ^> headless REAL testler
setlocal
cd /d "%~dp0.."

if exist ".venv\Scripts\python.exe" (
  set "PY=.venv\Scripts\python.exe"
) else (
  set "PY=python"
)

set "PATH=%CD%\tools\bin;%PATH%"
"%PY%" desktop_app\vibeshield_desktop.py %*
endlocal
