# 🛡️ VibeShield - Sadə UI Bələdçisi

## ✨ YENİ VERSİYA: Hər şey bir səhifədə!

**Nə dəyişdi?**
- ❌ Tab-lar arası keçid lazım deyil
- ✅ Hamısı bir ekranda
- ✅ Böyük, aydın düymələr
- ✅ Real-time nəticələr
- ✅ Rahat istifadə

---

## 🚀 BAŞLATMA

### Desktop İkonu (Tövsiyə)
```
1. Desktop-da "VibeShield" ikonunu tapın
2. Double-click
3. UI açılır
```

### Və ya Manuel
```bash
START_SIMPLE.bat

# və ya
cd desktop_app
python vibeshield_ui.py
```

---

## 📋 İLK DƏFƏ SETUP (3 dəqiqə)

### 1. API Key Əlavə Et
```
┌──────────────────────────────────┐
│ 🔑 OpenRouter API Key:           │
│ [sk-or-v1-...] 💾 Saxla 🧪 Test│
└──────────────────────────────────┘

Addımlar:
1. https://openrouter.ai-ya get
2. Sign Up (pulsuz!)
3. Create Key
4. Copy
5. UI-də yapışdır
6. 💾 Saxla
7. 🧪 Test → ✅
```

### 2. Projekt Seç
```
┌──────────────────────────────────┐
│ 📁 Projekt:                      │
│ [C:\...\target_app]  📂 Seç     │
└──────────────────────────────────┘

Addımlar:
1. 📂 Seç düyməsi
2. Folder seç (məsələn: target_app)
3. OK
```

### 3. Ready!
```
✅ API key təyin olunub
✅ Projekt seçildi
✅ Scan-a hazır!
```

---

## 🔧 TOOLLAR (6 Ədəd)

### ✓ Aktiv (Default)

**1. Audit Engine**
- Nə edir? 13 qayda, kod təhlili
- Zaman: ~10 san
- Misallar: Hardcoded secrets, SQL injection

**2. Gitleaks**
- Nə edir? Secret aşkarlanması
- Zaman: ~20 san
- Misallar: API keys, passwords, tokens

**3. Semgrep**
- Nə edir? SAST (30+ dil)
- Zaman: ~45 san
- Misallar: Security bugs, code smells

**4. Trivy**
- Nə edir? Dependency skan
- Zaman: ~30 san
- Misallar: CVE-lər, outdated packages

### □ Deaktiv (Seçmək Lazım)

**5. Strix AI** (LLM lazım)
- Nə edir? Real HTTP test, PoC yaradır
- Zaman: 5-15 dəq
- Misallar: IDOR, Auth bypass, SQL injection

**6. Nuclei**
- Nə edir? Template-based skan
- Zaman: 2-5 dəq
- Misallar: 5000+ vulnerability template

---

## 🚀 SCAN REJIMLƏRI

### 1️⃣ FULL SCAN (Tövsiyə)
```
🚀 FULL SCAN düyməsi

Nə edir?
✓ Statik skan (4 tool)
✓ Dinamik skan (Strix)
✓ Hamısı ardıcıl

Zaman: ~15 dəqiqə
```

### 2️⃣ Yalnız Statik
```
🔍 Statik düyməsi

Nə edir?
✓ Audit Engine
✓ Gitleaks
✓ Semgrep
✓ Trivy

Zaman: ~2 dəqiqə
```

### 3️⃣ Yalnız Pentest
```
🎯 Pentest düyməsi

Nə edir?
✓ Strix AI (LLM ilə)
✓ Real HTTP test
✓ PoC yaradır

Tələblər:
- API key
- Docker sandbox
- Target URL

Zaman: ~5 dəqiqə
```

---

## 📊 NƏTİCƏLƏR EKRANI

### Real-time Log

```
✨ VibeShield hazırdır!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚀 FULL SCAN BAŞLADI
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 STATİK SKAN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

▶️ [1/4] Audit Engine
  Ümumi:   4
  Kritik:  2
  Yüksək:  2
  ✅ Tamamlandı

▶️ [2/4] Gitleaks
  ⚠️ Secret-lər tapıldı!

▶️ [3/4] Semgrep
  ✅ Tamamlandı

▶️ [4/4] Trivy
  ✅ Tamamlandı

✅ Statik skan tamamlandı

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 DİNAMİK PENTEST
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

▶️ Strix AI Pentest
   Target: http://localhost:8000
   LLM: OpenRouter/Gemma-2-9B

   Test edilir:
   • IDOR
   • Auth Bypass
   • SQL Injection
   • Secret Exposure

✅ FULL SCAN TAMAMLANDI!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 💡 TƏLƏBLƏR

### P0 - Mütləq (Statik skan üçün)
```
✅ Python 3.8+
✅ pip install -e .
```

### P1 - Tövsiyə (Tam statik)
```
⚠️ pip install semgrep
⚠️ choco install gitleaks trivy
```

### P2 - Pentest üçün
```
🔑 OpenRouter API Key (pulsuz)
🐳 Docker (sandbox üçün)
🎯 Strix quraşdırılması
```

---

## 🐛 PROBLEM HƏLLİ

### UI açılmır
```bash
# Terminal-da işlədin
cd desktop_app
python vibeshield_ui.py

# Xəta mesajını oxuyun
```

### Tool quraşdırılmayıb
```bash
# Audit
pip install -e .

# Semgrep
pip install semgrep

# Gitleaks, Trivy
choco install gitleaks trivy -y
```

### API key işləmir
```
1. openrouter.ai-da yoxlayın
2. Yeni key yaradın
3. Copy/paste (boşluq yoxdur?)
4. 🧪 Test düyməsini klikləyin
```

### Pentest işləmir
```
1. API key var? (✅ status yuxarıda)
2. Docker işləyir? (docker ps)
3. Sandbox başladıb? (docker compose up)
4. Target URL düzgün?
```

---

## 🎯 İSTİFADƏ SSENARİSİ

### Gündəlik İstifadə
```
1. Desktop → VibeShield
2. Projekt seç (📂 Seç)
3. 🔍 Statik düyməsi
4. Gözlə (~2 dəq)
5. Nəticələrə bax
6. Düzəltmələr et
7. Yenidən skan
```

### Ətraflı Audit
```
1. Desktop → VibeShield
2. API key yoxla (✅ status)
3. Projekt seç
4. Docker başlat (ayrıca terminal)
5. 🚀 FULL SCAN
6. Gözlə (~15 dəq)
7. Statik + Dinamik nəticələr
8. PoC-ləri incələ
```

### CI/CD-yə Hazırlıq
```
1. Lokal full scan
2. Bütün zəiflikləri düzəlt
3. git push
4. GitHub Actions başlayır
5. Eyni scan pipeline-da
6. Gate keçərsə → deploy
```

---

## 📈 PERFORMANS

| Əməliyyat | Zaman |
|-----------|-------|
| Audit Engine | 10s |
| Gitleaks | 20s |
| Semgrep | 45s |
| Trivy | 30s |
| **Statik Total** | **~2m** |
| Strix AI | 5-15m |
| **Full Total** | **~15m** |

---

## ✅ ÜSTÜNLÜKLƏR

### Nə üçün bu UI?

✅ **Sadə** - Hər şey bir səhifədə  
✅ **Aydın** - Nə baş verir görünür  
✅ **Rahat** - Böyük düymələr  
✅ **Sürətli** - Tab-sız naviqasiya  
✅ **Real-time** - Canlı nəticələr  
✅ **Visual** - Tool kartları  

---

## 🎉 HAZIR!

Desktop-da "VibeShield" ikonuna klik edin!

```
Desktop → VibeShield (double-click)
```

Sadə, aydın və rahat UI istifadəyə hazırdır! 🚀
