@echo off
echo ============================================
echo   VibeShield Tools Installer
echo ============================================
echo.
echo This will install all security tools from the pipeline:
echo   - Semgrep (SAST)
echo   - Gitleaks (Secrets)
echo   - Trivy (SCA)
echo   - Nuclei (Templates)
echo   - Kavach-AI (Auto-fix)
echo   - DevSecOps-Radar (Reports)
echo.
cd desktop_app
python install_tools.py
echo.
echo ============================================
echo   Installation complete!
echo ============================================
echo.
echo Next: Restart terminal and run START_ENTERPRISE.bat
pause
