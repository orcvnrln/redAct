# VibeShield Complete Installer
# Installs: Docker, Gitleaks, Trivy, Nuclei, Semgrep

Write-Host "╔════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  VibeShield Complete Installer        ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$toolsDir = "$env:USERPROFILE\.vibeshield\tools"
New-Item -ItemType Directory -Force -Path $toolsDir | Out-Null

# ============================================================
# 1. SEMGREP (Python)
# ============================================================
Write-Host "📦 [1/5] Installing Semgrep..." -ForegroundColor Yellow
try {
    python -m pip install semgrep -q
    Write-Host "✅ Semgrep installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Semgrep failed" -ForegroundColor Red
}

# ============================================================
# 2. GITLEAKS (Binary)
# ============================================================
Write-Host ""
Write-Host "📦 [2/5] Installing Gitleaks..." -ForegroundColor Yellow
$gitleaksVersion = "8.18.1"
$gitleaksUrl = "https://github.com/gitleaks/gitleaks/releases/download/v$gitleaksVersion/gitleaks_${gitleaksVersion}_windows_x64.zip"
$gitleaksZip = "$toolsDir\gitleaks.zip"

try {
    Write-Host "  Downloading from GitHub..." -ForegroundColor Gray
    Invoke-WebRequest -Uri $gitleaksUrl -OutFile $gitleaksZip -UseBasicParsing
    
    Write-Host "  Extracting..." -ForegroundColor Gray
    Expand-Archive -Path $gitleaksZip -DestinationPath $toolsDir -Force
    Remove-Item $gitleaksZip
    
    if (Test-Path "$toolsDir\gitleaks.exe") {
        Write-Host "✅ Gitleaks installed: $toolsDir\gitleaks.exe" -ForegroundColor Green
    } else {
        Write-Host "❌ Gitleaks extraction failed" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Gitleaks download failed: $_" -ForegroundColor Red
}

# ============================================================
# 3. TRIVY (Binary)
# ============================================================
Write-Host ""
Write-Host "📦 [3/5] Installing Trivy..." -ForegroundColor Yellow
$trivyVersion = "0.48.3"
$trivyUrl = "https://github.com/aquasecurity/trivy/releases/download/v$trivyVersion/trivy_${trivyVersion}_Windows-64bit.zip"
$trivyZip = "$toolsDir\trivy.zip"

try {
    Write-Host "  Downloading from GitHub..." -ForegroundColor Gray
    Invoke-WebRequest -Uri $trivyUrl -OutFile $trivyZip -UseBasicParsing
    
    Write-Host "  Extracting..." -ForegroundColor Gray
    Expand-Archive -Path $trivyZip -DestinationPath $toolsDir -Force
    Remove-Item $trivyZip
    
    if (Test-Path "$toolsDir\trivy.exe") {
        Write-Host "✅ Trivy installed: $toolsDir\trivy.exe" -ForegroundColor Green
    } else {
        Write-Host "❌ Trivy extraction failed" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Trivy download failed: $_" -ForegroundColor Red
}

# ============================================================
# 4. NUCLEI (Binary)
# ============================================================
Write-Host ""
Write-Host "📦 [4/5] Installing Nuclei..." -ForegroundColor Yellow
$nucleiVersion = "3.1.5"
$nucleiUrl = "https://github.com/projectdiscovery/nuclei/releases/download/v$nucleiVersion/nuclei_${nucleiVersion}_windows_amd64.zip"
$nucleiZip = "$toolsDir\nuclei.zip"

try {
    Write-Host "  Downloading from GitHub..." -ForegroundColor Gray
    Invoke-WebRequest -Uri $nucleiUrl -OutFile $nucleiZip -UseBasicParsing
    
    Write-Host "  Extracting..." -ForegroundColor Gray
    Expand-Archive -Path $nucleiZip -DestinationPath $toolsDir -Force
    Remove-Item $nucleiZip
    
    if (Test-Path "$toolsDir\nuclei.exe") {
        Write-Host "✅ Nuclei installed: $toolsDir\nuclei.exe" -ForegroundColor Green
    } else {
        Write-Host "❌ Nuclei extraction failed" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Nuclei download failed: $_" -ForegroundColor Red
}

# ============================================================
# 5. DOCKER DESKTOP (Check/Prompt)
# ============================================================
Write-Host ""
Write-Host "📦 [5/5] Checking Docker..." -ForegroundColor Yellow

$dockerInstalled = Get-Command docker -ErrorAction SilentlyContinue

if ($dockerInstalled) {
    Write-Host "✅ Docker already installed" -ForegroundColor Green
    docker --version
} else {
    Write-Host "❌ Docker not found" -ForegroundColor Red
    Write-Host ""
    Write-Host "⚠️  Docker Desktop must be installed manually:" -ForegroundColor Yellow
    Write-Host "   https://www.docker.com/products/docker-desktop" -ForegroundColor Cyan
    Write-Host ""
    $response = Read-Host "Open Docker download page? (y/n)"
    if ($response -eq 'y') {
        Start-Process "https://www.docker.com/products/docker-desktop"
    }
}

# ============================================================
# ADD TO PATH
# ============================================================
Write-Host ""
Write-Host "📝 Adding tools to PATH..." -ForegroundColor Yellow

$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($currentPath -notlike "*$toolsDir*") {
    [Environment]::SetEnvironmentVariable("Path", "$currentPath;$toolsDir", "User")
    Write-Host "✅ Tools directory added to PATH" -ForegroundColor Green
    Write-Host "⚠️  Restart terminal/IDE to use tools" -ForegroundColor Yellow
} else {
    Write-Host "✅ Tools directory already in PATH" -ForegroundColor Green
}

# ============================================================
# SUMMARY
# ============================================================
Write-Host ""
Write-Host "╔════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║  Installation Complete!                ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "Installed tools:" -ForegroundColor Cyan
Write-Host "  ✅ Semgrep    (Python)" -ForegroundColor Green
Write-Host "  ✅ Gitleaks   $toolsDir\gitleaks.exe" -ForegroundColor Green
Write-Host "  ✅ Trivy      $toolsDir\trivy.exe" -ForegroundColor Green
Write-Host "  ✅ Nuclei     $toolsDir\nuclei.exe" -ForegroundColor Green

if ($dockerInstalled) {
    Write-Host "  ✅ Docker     Already installed" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  Docker    Manual install needed" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Restart terminal/IDE" -ForegroundColor White
Write-Host "  2. Run: START_ENTERPRISE.bat" -ForegroundColor White
Write-Host "  3. Test tools in UI" -ForegroundColor White
Write-Host ""
Write-Host "Tools directory: $toolsDir" -ForegroundColor Gray
Write-Host ""
