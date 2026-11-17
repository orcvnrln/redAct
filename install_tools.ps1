Write-Host "Installing VibeShield Tools..." -ForegroundColor Cyan

$toolsDir = "$env:USERPROFILE\.vibeshield\tools"
New-Item -ItemType Directory -Force -Path $toolsDir | Out-Null

# Semgrep
Write-Host "[1/4] Semgrep..." -ForegroundColor Yellow
python -m pip install semgrep -q
Write-Host "  OK" -ForegroundColor Green

# Gitleaks
Write-Host "[2/4] Gitleaks..." -ForegroundColor Yellow
$url = "https://github.com/gitleaks/gitleaks/releases/download/v8.18.1/gitleaks_8.18.1_windows_x64.zip"
Invoke-WebRequest -Uri $url -OutFile "$toolsDir\gitleaks.zip"
Expand-Archive -Path "$toolsDir\gitleaks.zip" -DestinationPath $toolsDir -Force
Remove-Item "$toolsDir\gitleaks.zip"
Write-Host "  OK" -ForegroundColor Green

# Trivy
Write-Host "[3/4] Trivy..." -ForegroundColor Yellow
$url = "https://github.com/aquasecurity/trivy/releases/download/v0.48.3/trivy_0.48.3_Windows-64bit.zip"
Invoke-WebRequest -Uri $url -OutFile "$toolsDir\trivy.zip"
Expand-Archive -Path "$toolsDir\trivy.zip" -DestinationPath $toolsDir -Force
Remove-Item "$toolsDir\trivy.zip"
Write-Host "  OK" -ForegroundColor Green

# Nuclei
Write-Host "[4/4] Nuclei..." -ForegroundColor Yellow
$url = "https://github.com/projectdiscovery/nuclei/releases/download/v3.1.5/nuclei_3.1.5_windows_amd64.zip"
Invoke-WebRequest -Uri $url -OutFile "$toolsDir\nuclei.zip"
Expand-Archive -Path "$toolsDir\nuclei.zip" -DestinationPath $toolsDir -Force
Remove-Item "$toolsDir\nuclei.zip"
Write-Host "  OK" -ForegroundColor Green

# Add to PATH
$env:Path += ";$toolsDir"
Write-Host ""
Write-Host "DONE! Tools in: $toolsDir" -ForegroundColor Green
Write-Host "Restart terminal and run: START_ENTERPRISE.bat" -ForegroundColor Cyan
