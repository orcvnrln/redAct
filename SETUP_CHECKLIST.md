# VibeShield — Quraşdırma və Yoxlama Siyahısı

## 📋 Komponent Statusu və Quraşdırma Təlimatı

### 1. Əsas Alətlər (Tools)

| Komponent | Vəziyyət | Quraşdırma | Qeyd |
|-----------|----------|------------|------|
| **Python 3.8+** | ✅ Quraşdırılıb (3.12.10) | - | Audit engine üçün tələb olunur |
| **Node.js 18+** | ⚠️ Yoxlanmalı | `node --version` | Target app üçün lazımdır |
| **Git** | ⚠️ Yoxlanmalı | `git --version` | GitHub Actions üçün |
| **Docker** | ⚠️ Yoxlanmalı | `docker --version` | Sandbox üçün tələb olunur |
| **jq** | ⚠️ Yoxlanmalı | Windows: `choco install jq` | Gate məntiqində JSON parser |

### 2. Təhlükəsizlik Skan Alətləri

| Alət | Vəziyyət | Quraşdırma | Nə üçün? |
|------|----------|------------|----------|
| **Audit Engine** | ✅ Hazır | `pip install -e .` | 13 regex qayda (bizim) |
| **Gitleaks** | ❌ Yoxdur | [Aşağıya bax](#gitleaks) | Secret aşkarlanması |
| **Semgrep** | ❌ Yoxdur | `pip install semgrep` | SAST (kod təhlili) |
| **Trivy** | ❌ Yoxdur | [Aşağıya bax](#trivy) | SCA (dependency skan) |
| **Strix** | ❌ Yoxdur | [Aşağıya bax](#strix) | AI pentest (LLM lazım) |
| **Nuclei** | ❌ Yoxdur | [Aşağıya bax](#nuclei) | Fallback pentest |
| **SonarQube** | ⚠️ İstəyə görə | [Aşağıya bax](#sonarqube) | Kod keyfiyyəti |

### 3. GitHub Secrets (API Keys)

| Secret | Vəziyyət | Necə əlavə edilir? | Pulsuz? |
|--------|----------|-------------------|---------|
| **OPENROUTER_API_KEY** | ❌ Təyin olunmayıb | [Aşağıya bax](#openrouter) | ✅ Bəli (pulsuz tier) |
| **GITHUB_TOKEN** | ✅ Avtomatik | GitHub tərəfindən verilir | ✅ Bəli |
| **SONAR_TOKEN** | ⚠️ İstəyə görə | SonarCloud-dan alın | ✅ Bəli (pulsuz tier) |
| **SONAR_HOST_URL** | ⚠️ İstəyə görə | `https://sonarcloud.io` | - |

---

## 🔧 Detallı Quraşdırma Təlimatları

### <a name="gitleaks"></a>Gitleaks (Secret Aşkarlanması)

#### Windows
```powershell
# Chocolatey ilə
choco install gitleaks

# Və ya manual
# 1. https://github.com/gitleaks/gitleaks/releases
# 2. gitleaks_windows_amd64.zip yükləyin
# 3. Extract edib PATH-a əlavə edin
```

#### Yoxlama
```bash
gitleaks version
# Gözlənilən: 8.x.x
```

#### Test
```bash
cd target_app
gitleaks detect --no-git --verbose
# Gözlənilən: Hardcoded secret tapmalıdır
```

---

### <a name="semgrep"></a>Semgrep (SAST)

#### Quraşdırma
```bash
pip install semgrep
```

#### Yoxlama
```bash
semgrep --version
# Gözlənilən: 1.x.x
```

#### Test
```bash
cd target_app
semgrep --config=auto --json .
# Gözlənilən: server.js-də zəifliklər tapmalıdır
```

---

### <a name="trivy"></a>Trivy (SCA - Dependency Skan)

#### Windows
```powershell
# Chocolatey ilə
choco install trivy

# Və ya manual
# 1. https://github.com/aquasecurity/trivy/releases
# 2. trivy_Windows-64bit.zip yükləyin
# 3. Extract edib PATH-a əlavə edin
```

#### Yoxlama
```bash
trivy --version
# Gözlənilən: 0.x.x
```

#### Test
```bash
trivy fs --severity HIGH,CRITICAL target_app/
# Gözlənilən: package.json asılılıqlarını skan etməli
```

---

### <a name="strix"></a>Strix (AI Pentest)

#### Quraşdırma
```bash
# Linux/Mac
curl -sSL https://strix.ai/install | bash

# Windows
# Manuel quraşdırma lazımdır - https://strix.ai/docs
```

#### Yoxlama
```bash
strix --version
# Gözlənilən: 2.x.x
```

#### ⚠️ LLM API Key Lazımdır
Strix işləməsi üçün OpenRouter API key lazımdır (aşağıya bax).

#### Test
```bash
# Sandbox işləyir və API key təyin olunub olarsa
export LLM_API_KEY="sk-or-v1-..."
export STRIX_LLM="openrouter/google/gemma-2-9b-it"
strix -n --target http://localhost:8000 --scan-mode quick
```

---

### <a name="nuclei"></a>Nuclei (Fallback Pentest)

#### Windows
```powershell
# Go ilə
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest

# Və ya binary yükləyin
# https://github.com/projectdiscovery/nuclei/releases
```

#### Yoxlama
```bash
nuclei -version
# Gözlənilən: v3.x.x
```

#### Test
```bash
nuclei -u http://localhost:8000 -t exposures/
# Gözlənilən: Debug endpoint tapmalıdır
```

---

### <a name="sonarqube"></a>SonarQube / SonarCloud (Kod Keyfiyyəti)

#### ⚠️ İSTƏYƏ GÖRƏ

Pipeline işləməsi üçün lazım **deyil**, lakin kod keyfiyyəti üçün tövsiyə olunur.

#### SonarCloud Quraşdırma (Pulsuz)

1. https://sonarcloud.io-ya daxil olun
2. GitHub ilə login edin
3. "+" → "Analyze new project"
4. Repository seçin
5. **SONAR_TOKEN** alın
6. GitHub Secrets-ə əlavə edin

#### Lokal Sonar Scanner (İstəyə görə)
```bash
# Windows
choco install sonarscanner

# Test
sonar-scanner --version
```

---

### <a name="openrouter"></a>OpenRouter API Key (Strix və AI Chat üçün)

#### 1. Qeydiyyat (PULSUZ)
1. https://openrouter.ai-ya keçin
2. Google və ya GitHub ilə sign up edin
3. **Kredit kartı LAZIM DEYIL**

#### 2. API Key Alın
1. Dashboard → Keys
2. "Create Key" klikləyin
3. Adı: `vibeshield-dev`
4. Key-i kopyalayın: `sk-or-v1-...`

#### 3. Pulsuz Model
- **Gemma 2 9B IT**: `openrouter/google/gemma-2-9b-it`
- Limit: 20 request/dəqiqə
- Cost: **$0.00** (pulsuz tier)

#### 4. GitHub Secrets-ə Əlavə Edin
```
Repository → Settings → Secrets and variables → Actions
→ New repository secret
   Name: OPENROUTER_API_KEY
   Value: sk-or-v1-...
```

#### 5. Desktop UI-da Konfiqurasiya
```
Desktop App → ⚙️ Konfiqurasiya tab
→ OpenRouter API Açarı: sk-or-v1-...
→ Model: openrouter/google/gemma-2-9b-it
→ 💾 Konfiqurasiyaı yadda saxla
```

---

## 🚀 Sürətli Quraşdırma Skripti (Windows)

```powershell
# 1. Python paketləri
pip install -e .
pip install semgrep requests pyyaml

# 2. Node.js asılılıqları
cd target_app
npm install
cd ..

# 3. Chocolatey alətləri (admin hüquqları lazımdır)
choco install gitleaks trivy jq -y

# 4. Nuclei (Go lazımdır)
# go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest

# 5. Docker-i yoxla
docker --version
# Yoxdursa: https://www.docker.com/products/docker-desktop

# 6. Git-i yoxla
git --version
```

---

## ✅ Yoxlama Skripti

Sisteminizin hazır olub-olmadığını yoxlayın:

```bash
# Windows PowerShell
python scripts/check_system.py
```

və ya manual:

```powershell
Write-Host "=== VibeShield System Check ===" -ForegroundColor Cyan

# Python
python --version
if ($?) { Write-Host "✓ Python quraşdırılıb" -ForegroundColor Green } 
else { Write-Host "✗ Python yoxdur" -ForegroundColor Red }

# Node.js
node --version
if ($?) { Write-Host "✓ Node.js quraşdırılıb" -ForegroundColor Green }
else { Write-Host "✗ Node.js yoxdur" -ForegroundColor Red }

# Docker
docker --version
if ($?) { Write-Host "✓ Docker quraşdırılıb" -ForegroundColor Green }
else { Write-Host "✗ Docker yoxdur" -ForegroundColor Red }

# Git
git --version
if ($?) { Write-Host "✓ Git quraşdırılıb" -ForegroundColor Green }
else { Write-Host "✗ Git yoxdur" -ForegroundColor Red }

# jq
jq --version
if ($?) { Write-Host "✓ jq quraşdırılıb" -ForegroundColor Green }
else { Write-Host "✗ jq yoxdur (choco install jq)" -ForegroundColor Red }

# Gitleaks
gitleaks version
if ($?) { Write-Host "✓ Gitleaks quraşdırılıb" -ForegroundColor Green }
else { Write-Host "✗ Gitleaks yoxdur" -ForegroundColor Red }

# Semgrep
semgrep --version
if ($?) { Write-Host "✓ Semgrep quraşdırılıb" -ForegroundColor Green }
else { Write-Host "✗ Semgrep yoxdur (pip install semgrep)" -ForegroundColor Red }

# Trivy
trivy --version
if ($?) { Write-Host "✓ Trivy quraşdırılıb" -ForegroundColor Green }
else { Write-Host "✗ Trivy yoxdur" -ForegroundColor Red }

# Audit Engine
python -m audit.run_audit --help
if ($?) { Write-Host "✓ Audit Engine hazırdır" -ForegroundColor Green }
else { Write-Host "✗ Audit Engine quraşdırılmayıb (pip install -e .)" -ForegroundColor Red }

Write-Host "`n=== API Keys ===" -ForegroundColor Cyan
Write-Host "GitHub Secrets yoxlamaq üçün: Repository → Settings → Secrets" -ForegroundColor Yellow
```

---

## 🎯 Minimal İşləyən Konfiqurasiya

Pipeline işləməsi üçün **minimal tələblər**:

### ✅ Mütləq Lazım
1. ✅ Python 3.8+ (quraşdırılıb)
2. ⚠️ Node.js 18+ (yoxlanmalı)
3. ⚠️ Docker (sandbox üçün)
4. ⚠️ Git (GitHub Actions üçün)
5. ⚠️ jq (gate məntiqində)
6. ❌ Audit Engine dependencies: `pip install -e .`

### ⚠️ Tövsiyə Olunan (Statik Qat)
7. ❌ Gitleaks
8. ❌ Semgrep: `pip install semgrep`
9. ❌ Trivy

### 🔵 İstəyə Görə (Dinamik Qat)
10. ❌ Strix + OpenRouter API key
11. ❌ Nuclei (fallback)
12. ⚠️ SonarQube (kod keyfiyyəti)

---

## 📊 Prioritet Sırası

### P0 (İndi quraşdırın)
```powershell
# 1. Audit engine və Python asılılıqları
pip install -e .
pip install semgrep

# 2. Node.js asılılıqları
cd target_app
npm install
cd ..

# 3. Docker-i yoxla/quraşdır
docker --version
```

### P1 (Statik skan üçün)
```powershell
# Chocolatey admin hüquqları ilə
choco install gitleaks trivy jq -y
```

### P2 (Dinamik skan üçün)
1. OpenRouter API key alın (https://openrouter.ai)
2. GitHub Secrets-ə əlavə edin
3. Strix quraşdırın (Linux/Mac)

### P3 (Kod keyfiyyəti)
1. SonarCloud qeydiyyat
2. SONAR_TOKEN əlavə edin

---

## 🐛 Çox Rast Gəlinən Problemlər

### 1. "npm: command not found"
**Həll:** Node.js quraşdırın - https://nodejs.org

### 2. "docker: command not found"
**Həll:** Docker Desktop quraşdırın - https://www.docker.com/products/docker-desktop

### 3. "jq: command not found"
**Həll:** 
```powershell
choco install jq -y
# və ya manual: https://stedolan.github.io/jq/download/
```

### 4. "pip install semgrep" xətası
**Həll:** Python 3.8+ olduğundan əmin olun
```bash
python --version  # 3.8+
pip install --upgrade pip
pip install semgrep
```

### 5. Strix quraşdırılmır (Windows)
**Həll:** Strix əsasən Linux/Mac üçündür. Alternativ:
- WSL2 istifadə edin
- Və ya Strix-i deaktiv edin (Nuclei fallback işləyəcək)
- Və ya GitHub Actions-da işlədin (Linux runner)

### 6. "OPENROUTER_API_KEY not found"
**Həll:** 
- Lokal: Desktop UI → Konfiqurasiya → API key daxil edin
- CI/CD: GitHub Secrets-ə əlavə edin

---

## 📝 Növbəti Addımlar

1. ✅ Bu faylı oxuyun
2. ⚠️ Yuxarıdakı yoxlama skriptini işlədin
3. ⚠️ Çatışmayan alətləri quraşdırın (P0 → P1)
4. ⚠️ OpenRouter API key alın
5. ⚠️ GitHub Secrets konfiqurasiyası
6. ✅ `git push` → GitHub Actions-da pipeline-ı izləyin

---

## 🔗 Faydalı Linklər

- **Gitleaks:** https://github.com/gitleaks/gitleaks
- **Semgrep:** https://semgrep.dev
- **Trivy:** https://github.com/aquasecurity/trivy
- **Strix:** https://strix.ai
- **Nuclei:** https://github.com/projectdiscovery/nuclei
- **OpenRouter:** https://openrouter.ai
- **SonarCloud:** https://sonarcloud.io
- **Docker Desktop:** https://www.docker.com/products/docker-desktop
- **Node.js:** https://nodejs.org
- **jq:** https://stedolan.github.io/jq

---

**Qeyd:** Bütün alətləri quraşdırmaq məcburi deyil. Minimal konfiqurasiya ilə (Python + Audit Engine) sistem işləyir, lakin tam təhlükəsizlik üçün bütün alətlər tövsiyə olunur.
