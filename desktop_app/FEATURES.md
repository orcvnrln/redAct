# Desktop UI — Xüsusiyyətlər və İstifadə Təlimatı

## 🎯 Ümumi Baxış

VibeShield Desktop UI — VS Code tipli, tab-əsaslı təhlükəsizlik idarəetmə panelidir. 8 əsas bölmədən ibarətdir:

1. **⚙️ Konfiqurasiya** — API key, target URL, alət seçimi
2. **🔑 API Keys** — OpenRouter, GitHub, SonarCloud key idarəetməsi
3. **📁 Projektlər** — Fayl/folder brauzer və idarəetmə
4. **🔍 Skanlar** — Bütün təhlükəsizlik skanlarını işə salma
5. **🚪 Deterministik Qapı** — Unified findings təhlili
6. **🤖 AI Chat** — Təhlükəsizlik məsləhətçisi
7. **📄 Hesabat** — PDF və JSON hesabatlar
8. **📋 Loglar** — Sistem logları

---

## 🚀 Başlatma

### Windows Desktop Shortcut (Tövsiyə)

```powershell
# İkon yaradın
PowerShell -ExecutionPolicy Bypass -File create_desktop_shortcut.ps1

# Desktop-da "VibeShield Desktop" ikonuna double-click edin
```

### Manual Başlatma

```bash
# Method 1: Batch file (Windows)
cd desktop_app
run.bat

# Method 2: Python birbaşa
cd desktop_app
python main.py
```

---

## 1️⃣ Konfiqurasiya Tab

### Parametrlər

- **OpenRouter API Açarı:** `sk-or-v1-...` (pulsuz tier)
- **Model:** `openrouter/google/gemma-2-9b-it` (default)
- **API Base URL:** `https://openrouter.ai/api/v1`
- **Hedef URL:** `http://localhost:8000` (sandbox target)

### Aktiv Alətlər

- ☑️ Strix AI Pentest (LLM lazımdır)
- ☑️ Nuclei (LLM-siz fallback)
- ☑️ Semgrep SAST
- ☑️ Trivy SCA
- ☑️ Gitleaks Secrets
- ☐ SonarQube (istəyə görə)

### Qapı Səviyyəsi

- Default: `critical,high`
- Bu severity-lər tapılsa qapı bloklanır

### Yadda Saxlama

Bütün konfiqurasiya `config.json` faylında saxlanılır.

---

## 2️⃣ API Keys Tab (YENİ!)

### Xüsusiyyətlər

#### 🔑 OpenRouter API Key (Mütləq)
- **Status göstəricisi:** ✅/❌ təyin olunub/olunmayıb
- **Masked display:** `sk-or-v1-xxxxx...xxxx` (təhlükəsizlik üçün)
- **Show/Hide toggle:** Key-i görmək üçün checkbox
- **Yadda Saxla:** config.json-a yazır
- **Test Et:** API key-in düzgünlüyünü yoxlayır (models endpoint)
- **OpenRouter-a Get:** Browser-də openrouter.ai açır
- **Təmizlə:** Key-i silir

**Test funksiyası:**
- `https://openrouter.ai/api/v1/models` sorğusu göndərir
- Status 200 → ✅ Key düzgündür
- Status 401/403 → ❌ Key yanlışdır
- Model sayını göstərir

#### 🔑 GitHub Token (GitHub Actions üçün)
- **Avtomatik:** GitHub Actions-da `GITHUB_TOKEN` avtomatik verilir
- **Lokal:** Personal Access Token yaratmaq üçün link
- **Scope-lar:** repo, workflow
- **GitHub Token Yarat** düyməsi → browser-də açır

#### 🔑 SonarCloud Token (İstəyə görə)
- **Status:** ✅/⚠️ təyin olunub/olunmayıb (istəyə görə)
- **Masked display:** Token gizlədilir
- **Yadda Saxla:** config.json-a yazır
- **SonarCloud-a Get:** Browser-də sonarcloud.io açır

#### 📋 GitHub Secrets Helper
- **Auto-detect:** Git remote-dan repository URL-ni tapır
- **Direct link:** `github.com/<user>/<repo>/settings/secrets/actions`
- **Təlimat:** Secret əlavə etmək üçün addım-addım

### İstifadə Ssenarisi

```
1. [API Keys] tab-ına keçin
2. OpenRouter API Key daxil edin: sk-or-v1-...
3. "💾 Yadda Saxla" klikləyin
4. "🧪 Test Et" klikləyin (yoxlama üçün)
5. ✅ Status: "Təyin olunub: sk-or-v1-xxxxx...xxxx"
6. "🌐 Repository Secrets-ə Get" → GitHub Secrets-ə əlavə edin
7. [AI Chat] tab-ında AI-dan istifadə edə bilərsiniz
```

---

## 3️⃣ Projektlər Tab (YENİ!)

### Xüsusiyyətlər

#### 📁 Projekt Aç
- Lokal kataloqu seçin
- Bütün fayl/folderləri tree view-də görünür
- Lazy loading (folderləri tıklayanda açılır)

#### ➕ Fayl Əlavə Et
- Dialog açılır
- Fayl adı və extension seçin
- Default content: `# Yeni fayl\n`
- Avtomatik tree-yə əlavə olunur

#### ➕ Folder Əlavə Et
- Folder adı dialog-da yazın
- Projekt root-da yaradılır
- Avtomatik tree-yə əlavə olunur

#### 🗑️ Sil
- Tree-dən fayl/folder seçin
- Təsdiq dialoqundan sonra silinir
- Folder silinmə recursive-dir

#### 📄 Fayl Önizləmə
- Tree-dən fayl seçin (tək klik)
- Sağ paneldə ilk 10KB görünür
- UTF-8 encoding, errors=ignore

#### Qısayollar
- Folder-ə **Double Click** → Expand/Collapse
- Fayl-a **Single Click** → Önizləmə

---

## 4️⃣ Skanlar Tab

### Bütün Skanları İşlət

Aktiv alətləri ardıcıl işlədir:

1. Gitleaks → secrets.json
2. Semgrep → semgrep.json
3. Trivy → trivy.json
4. Strix (API key varsa) → findings.json
5. Nuclei (Strix uğursuzsa) → nuclei.json

### Nəticələr

Tree view-də hər alət üçün:
- ✅/❌ Status
- Çıxış (ilk 120 simvol)
- Fayl yolu
- Xəta mesajı

Alət seçdikdə, tam JSON nəticəsi alt paneldə görünür.

---

## 5️⃣ Deterministik Qapı Tab

### 🔗 Nəticələri Birləşdir

Bütün scan fayllarını (`semgrep.json`, `trivy.json`, `findings.json`, `nuclei.json`) oxuyub `unified_findings.json` yaradır.

Format:
```json
{
  "findings": [
    {"tool": "audit_engine", "severity": "critical", "title": "Hardcoded API Key", ...},
    {"tool": "strix", "severity": "high", "title": "IDOR", ...}
  ],
  "count": 42
}
```

### 🚪 Qapını Dəyərləndir

`unified_findings.json`-dakı `critical` və `high` severity-ləri sayır:

- **0** → ✅ **PUBLISH-Ə İCAZƏ VERİLİR**
- **> 0** → ❌ **PUBLISH BLOKLANDI**

### Qərar Məntiqinin Təsdiqi

```python
CRITICAL = len([f for f in findings if f['severity'] in ['critical', 'high']])
if CRITICAL > 0:
    decision = "BLOK"
else:
    decision = "KEÇ"
```

**LLM bu qərara müdaxilə etmir** — yalnız JSON-dan oxunur.

---

## 6️⃣ AI Chat Tab (YENİ!)

### Xüsusiyyətlər

#### 🤖 OpenRouter İnteqrasiyası

API key konfiqurasiyada təyin olunubsa:
1. User mesajı alır
2. `unified_findings.json` və projekt məlumatını context kimi göndərir
3. OpenRouter/Gemma-2-9B-IT-dən cavab alır
4. Azərbaycan dilində cavab qaytarır

#### 🔌 Lokal Fallback

API key yoxdursa:
1. Lokal məlumatı oxuyur (`unified_findings.json`)
2. Keyword əsaslı sadə cavablar verir
3. Məsələn: "IDOR" keyword-u tapılsa → IDOR düzəltmə təlimatı

#### Hazır Suallar

1. "unified_findings.json-dakı ən kritik zəifliyi izah et"
2. "IDOR zəifliyini necə düzəldə bilərəm?"
3. "Hardcoded secret-ləri necə təmizləyim?"
4. "Bu proyektdə hansı OWASP Top 10 zəiflikləri var?"

#### Chat Interface

- **👤 Siz:** (mavi, bold)
- **🤖 AI:** (yaşıl)
- **Enter** → Mesaj göndər
- **🗑️ Təmizlə** → Chat history silinir

#### Context Məlumatı

AI-ya göndərilən context:
```
Tapıntı sayı: 5
Kritik: 2, Yüksək: 3

Ən vacib tapıntılar:
- audit_engine: Hardcoded API Key (critical)
- strix: IDOR (high)
- semgrep: SQL Injection (high)

Cari projekt: C:\Users\...\ssimi
```

---

## 7️⃣ Hesabat Tab

### PDF Hesabatı

`report.pdf` mövcud olarsa, yol göstərilir.

### Unified Findings

`unified_findings.json` content-i göstərilir (JSON formatında).

---

## 8️⃣ Loglar Tab

Bütün UI əməliyyatları log-lanır:
- Konfiqurasiya dəyişikliyi
- Skan başlama/bitirmə
- Fayl/folder əlavə/silmə
- AI chat sorğuları

---

## 🎮 İstifadə Ssenariləri

### Ssenarı 1: Lokal Proyekt Skan

```
1. [Projektlər] → "📁 Projekt Aç" → target_app seçin
2. [Konfiqurasiya] → API key əlavə edin (istəyə görə)
3. [Skanlar] → "🚀 Bütün aktiv skanları işlət"
4. [Qapı] → "🔗 Nəticələri Birləşdir"
5. [Qapı] → "🚪 Qapını Dəyərləndir"
6. ✅ və ya ❌ qərarını görün
```

### Ssenarı 2: AI ilə Zəiflik Təhlili

```
1. [Qapı] → "🔗 Nəticələri Birləşdir" (context üçün)
2. [AI Chat] → Hazır sual seçin və ya öz sualınızı yazın
3. 🤖 AI cavabı alın
4. Təlimatları tətbiq edin
5. Yenidən skan edin
```

### Ssenarı 3: Yeni Fayl Yaratma

```
1. [Projektlər] → "📁 Projekt Aç"
2. "➕ Fayl Əlavə Et"
3. Fayl adı: test.js
4. Avtomatik açılır və təmiz content ilə yaradılır
5. Önizləmədə görünür
```

---

## 🔧 Texniki Detallar

### Arxitektura

```
┌─────────────────────────────────────────┐
│         DevSecOpsDesktopApp             │
│  ┌────────────────────────────────┐     │
│  │  DesktopScanner                │     │
│  │  (run_all_local, get_results)  │     │
│  └────────────────────────────────┘     │
│  ┌────────────────────────────────┐     │
│  │  DeterministicGate             │     │
│  │  (unify_findings, evaluate)    │     │
│  └────────────────────────────────┘     │
│  ┌────────────────────────────────┐     │
│  │  AI Chat (OpenRouter)          │     │
│  │  (_get_ai_response, context)   │     │
│  └────────────────────────────────┘     │
└─────────────────────────────────────────┘
```

### Asılılıqlar

```python
# Standard library
import tkinter
import json
import os

# External
import requests  # AI Chat üçün
import yaml      # Konfiqurasiya üçün
```

### Konfiqurasiya Faylı

`desktop_app/config.json`:
```json
{
  "openrouter_api_key": "sk-or-v1-...",
  "openrouter_model": "openrouter/google/gemma-2-9b-it",
  "openrouter_base": "https://openrouter.ai/api/v1",
  "target_url": "http://localhost:8000",
  "current_project": "C:\\Users\\...\\ssimi",
  "tools": {
    "strix": true,
    "nuclei": true,
    "semgrep": true,
    "trivy": true,
    "gitleaks": true,
    "sonarqube": false
  },
  "severity_threshold": ["critical", "high"],
  "paths": {
    "semgrep_json": "semgrep.json",
    "trivy_json": "trivy.json",
    "findings_json": "findings.json",
    "nuclei_json": "nuclei.json",
    "unified_findings_json": "unified_findings.json",
    "report_pdf": "report.pdf"
  }
}
```

---

## 🚀 Performans

- **UI responsiveness:** Bütün skan əməliyyatları non-blocking deyil (threading lazımdır)
- **File tree:** Lazy loading ilə min-lərlə fayl dəstəklənir
- **AI Chat:** 1-3 saniyə (OpenRouter latency)
- **Lokal fallback:** <100ms

---

## 🔐 Təhlükəsizlik

- API key `config.json`-da saxlanılır (lokal fayl)
- Password field (`show="*"`) istifadə olunur
- Fayl silinmə confirmation dialog-u var
- AI Chat-da heç bir code execution yoxdur (yalnız cavab text)

---

## 🐛 Debug

### Loglar

Bütün əməliyyatlar **📋 Loglar** tab-ında görünür. Məsələn:
```
Uygulama başlatıldı.
Projekt açıldı: C:\Users\...\ssimi
Fayl yaradıldı: C:\Users\...\ssimi\test.js
AI Chat | User: IDOR necə düzəldim? | AI: Ownership yoxlaması...
```

### Xəta halları

- **API key yoxdur:** Lokal fallback
- **Fayl tapılmadı:** Warning dialog
- **Scan tool yoxdur:** Error mesajı scan tree-də
- **Network timeout:** 30 saniyə sonra xəta

---

## 💡 Tövsiyələr

1. **İlk dəfə:** Əvvəl Konfiqurasiya tab-ında bütün parametrləri təyin edin
2. **Skan:** Sandbox işləyirsə (docker-compose up), target URL-ni `http://localhost:8000` edin
3. **AI Chat:** API key olmasa da lokal cavablar əldə edə bilərsiniz
4. **Projekt Manager:** Böyük projektlərdə tree lazy load olur, səbir edin

---

## 🎨 UI Elementləri

| Element | Tip | Rəng |
|---------|-----|------|
| User message | Text | Mavi, bold |
| AI response | Text | Yaşıl |
| Error | Text | Qırmızı |
| Gate PASS | Text | Yaşıl |
| Gate FAIL | Text | Qırmızı |
| Status bar | Label | Gri |

---

## 📚 Əlavə Resurslar

- OpenRouter pulsuz tier: https://openrouter.ai/docs#free-tier
- Gemma 2 9B model: https://openrouter.ai/models/google/gemma-2-9b-it
- Tkinter docs: https://docs.python.org/3/library/tkinter.html

---

**Qeyd:** Desktop UI Windows, Linux və macOS-da işləyir. Tkinter Python-la birlikdə gəlir, əlavə quraşdırma lazım deyil.
