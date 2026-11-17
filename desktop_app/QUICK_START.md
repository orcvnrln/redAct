# 🚀 VibeShield Pro - Quick Start

## ✅ SETTINGS FIX TAMAMLANDI!

### Problem nə idi?
- SETTINGS hissəsi işləmirdi
- API key config-də olsa belə UI-da görünmürdü
- Hər dəfə yenidən SET etməli idin

### İndi nə düzəldi?
- ✅ API key avtomatik yüklənir və göstərilir
- ✅ Project path avtomatik yüklənir
- ✅ Green/Red vizual feedback
- ✅ Təhlükəsiz göstərim (masked)

## 🎯 Test Et

### 1. Config Yoxla
```bash
cd desktop_app
python test_settings.py
```

Görəcəksən:
```
✓ Config file found and loaded
✓ API Key exists!
  Display format: sk-test-12...wxyz
  Status: GREEN (Success)
```

### 2. UI-ı Başlat
```bash
python vibeshield_pro.py
```

Və ya:
```bash
TEST_UI.bat
```

### 3. Yoxla
UI açılanda:
- **API Key** → ✓ GREEN (sk-test-12...wxyz)
- **Project Path** → C:\Users\Spark\Desktop\ssimi

## 📋 İstifadə

### İlk Dəfə
1. UI-ı aç
2. API Key yoxdursa → SET et
3. Project seç → 📂 düyməsi
4. 🚀 FULL ORCHESTRATED SCAN bas

### Növbəti Dəfə
1. UI-ı aç
2. Hər şey artıq yüklənib (GREEN ✓)
3. Birbaşa SCAN bas

## 🎨 Görünüş

```
╔══════════════════════════════════════════╗
║        ⚙️ CONFIGURATION                  ║
╠══════════════════════════════════════════╣
║                                          ║
║  ✓ API Key: sk-test-12...wxyz  [GREEN]  ║
║  [**********************] [SET]          ║
║                                          ║
║  📁 Project Path:                        ║
║  [C:\Users\Spark\Desktop\ssimi] [📂]     ║
║                                          ║
╠══════════════════════════════════════════╣
║        🔧 SECURITY TOOLS                 ║
╠══════════════════════════════════════════╣
║  ● ✓ Audit Engine      13 Rules         ║
║  ● 🔐 Gitleaks         Secrets           ║
║  ● 🧬 Semgrep          SAST              ║
║  ● 📦 Trivy            SCA               ║
║  ● 🎯 Strix AI         Pentest           ║
║  ● ⚡ Nuclei           Templates         ║
╚══════════════════════════════════════════╝
```

## 🔧 Config Format

`config.json`:
```json
{
  "openrouter_api_key": "sk-...",
  "target_url": "http://localhost:8000",
  "project_path": "C:\\Users\\Spark\\Desktop\\ssimi"
}
```

## ⚡ Qısa Yollar

### Desktop Icon
Double-click: **VibeShield** ikonu

### Batch Files
- `TEST_UI.bat` - Test + Launch
- `START_SIMPLE.bat` - Sadəcə Launch

### Python Direct
```bash
cd desktop_app
python vibeshield_pro.py
```

## 📊 Status Indicators

| Icon | Status | Mənası |
|------|--------|--------|
| ✓ GREEN | Success | API key set, tool available |
| ✗ RED | Error | API key missing, tool not found |
| ● GREEN | Online | Tool available and working |
| ● RED | Offline | Tool not installed |
| ● GRAY | Unknown | Not tested yet |

## 🎯 Next Steps

1. ✅ Test settings loading → `python test_settings.py`
2. ✅ Launch UI → `python vibeshield_pro.py`
3. ⚙️ Verify API key shows GREEN
4. 📁 Verify project path shows
5. 🧪 Test all tools → "🧪 TEST ALL TOOLS" button
6. 🚀 Run scan → "⚡ FULL ORCHESTRATED SCAN"
7. 💻 Watch terminal output
8. 📊 Check results tab

## 🐛 Troubleshooting

### API Key hələ görünmür?
```bash
# Config-i yoxla
cat desktop_app/config.json

# Python-də test et
cd desktop_app
python test_settings.py
```

### Tools RED görünür?
- Normal! Toollar quraşdırılmayıb
- Audit Engine işləməlidir (GREEN)
- Qalanları quraşdırmaq istəyirsənsə:
  - `gitleaks`: https://github.com/gitleaks/gitleaks
  - `semgrep`: https://semgrep.dev
  - `trivy`: https://trivy.dev
  - `strix`: Custom tool (bizim repo)

### Scan işləmir?
- API key set edilib? (GREEN ✓)
- Project path düzgün? (folder mövcuddur?)
- Test tools düyməsini basdın?

## ✨ Features Working

- ✅ Deep dark theme
- ✅ Terminal orchestration
- ✅ AI assistant
- ✅ API key auto-load **[YENİ]**
- ✅ Project path auto-load
- ✅ Tool testing
- ✅ Live color output
- ✅ Sequential stages

---
**Status**: ✅ READY TO USE
**Version**: 2.0 (Settings Fixed)
**Date**: 2026-11-17
