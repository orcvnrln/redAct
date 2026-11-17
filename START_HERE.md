# 🚀 VibeShield Desktop - Başlatma Təlimatı

## ✅ Desktop App-ı Açmaq (3 Yol)

### 🔥 YOL 1: Desktop İkon (Ən Asan)

```
1. Desktop-da "VibeShield Desktop" ikonunu tapın
2. İkona DOUBLE-CLICK edin
3. Terminal açılacaq və sonra Desktop UI pencerəsi görünəcək
4. Terminal-ı bağlaya bilərsiniz (X), UI işləyəcək
```

**İkon yoxdursa?**
```powershell
PowerShell -ExecutionPolicy Bypass -File create_desktop_shortcut.ps1
```

---

### 🔥 YOL 2: Python Launcher (Tövsiyə)

```bash
python launch_desktop.py
```

**Nə edir?**
- Desktop UI-ni background-da başladır
- Terminalı bağlaya bilərsiniz
- UI işləməyə davam edər

---

### 🔥 YOL 3: Manuel (Hər zaman işləyir)

```bash
cd desktop_app
python main.py
```

və ya Windows-da:
```bash
cd desktop_app
run.bat
```

**Qeyd:** Bu yolla terminal bağlansa, UI də bağlanar.

---

## 🎯 İlk Dəfə Açıldıqda Nə Etmək?

### Addım 1: Test Edin
```
1. Desktop UI açıldı?
2. Bütün tab-lar görünür?
   - ⚙️ Konfiqurasiya
   - 🔑 API Keys
   - 📁 Projektlər
   - 🔍 Skanlar
   - 🚪 Qapı
   - 🤖 AI Chat
   - 📄 Hesabat
   - 📋 Loglar
```

### Addım 2: API Key Əlavə Edin
```
1. 🔑 API Keys tab-ına keçin
2. OpenRouter API Key input-una yapışdırın: sk-or-v1-...
3. "💾 Yadda Saxla" düyməsini klikləyin
4. "🧪 Test Et" ilə yoxlayın
5. ✅ "Təyin olunub" mesajı görməlisiniz
```

**API Key almadınız?**
```
1. https://openrouter.ai
2. Sign Up (Google/GitHub)
3. Dashboard → Keys → Create Key
4. Copy: sk-or-v1-...
```

### Addım 3: Projekt Açın
```
1. 📁 Projektlər tab
2. "📁 Projekt Aç" düyməsi
3. target_app folder-ini seçin
4. Fayl tree görünəcək
```

### Addım 4: Skan İşlədin
```
1. 🔍 Skanlar tab
2. "🚀 Bütün aktiv skanları işlət"
3. Gözləyin (30-60 saniyə)
4. Nəticələr tree-də görünəcək
```

### Addım 5: AI-dan İstifadə Edin
```
1. 🤖 AI Chat tab
2. Hazır sual seçin və ya öz sualınızı yazın
3. Enter
4. 🤖 AI cavabı oxuyun
```

---

## 🐛 Problem Həlli

### "Pencere açılmır"

**Həll 1:** Terminal-da manual başladın
```bash
cd desktop_app
python main.py
```

**Həll 2:** Python path-i yoxla
```bash
python --version
# Görməlisiniz: Python 3.x.x
```

**Həll 3:** Tkinter yoxla
```bash
python -c "import tkinter; print('OK')"
# Görməlisiniz: OK
```

---

### "Python tapılmadı"

**Həll:**
```
1. https://www.python.org/downloads/
2. Python 3.8+ yükləyin
3. "Add Python to PATH" ✓ checkbox
4. Install
5. PowerShell-i yenidən açın
```

---

### "Tkinter import xətası"

**Həll (Windows):**
```
1. Python installer-ı yenidən işə salın
2. "Modify"
3. "Optional Features" → "tcl/tk and IDLE" ✓
4. Install
```

---

### UI açılır amma boş

**Həll:**
```bash
# Test skriptini işlət
cd desktop_app
python test_ui.py

# Xətanı görəcəksiniz
```

---

## 📊 Sistem Yoxlaması

Desktop app işləməsi üçün:

```bash
# Avtomatik yoxlama
python scripts/check_system.py

# Manual yoxlama
python --version        # ✓ 3.12.10
python -c "import tkinter"  # ✓ OK
cd desktop_app
python test_ui.py       # ✓ Bütün testlər
```

---

## 💡 Faydalı Komandalar

```bash
# Desktop shortcut yarat
PowerShell -ExecutionPolicy Bypass -File create_desktop_shortcut.ps1

# UI-ni background-da başlat
python launch_desktop.py

# UI-ni birbaşa başlat
cd desktop_app
python main.py

# Test et
cd desktop_app
python test_ui.py

# Sistem yoxla
python scripts/check_system.py
```

---

## 📁 Başlatma Faylları

| Fayl | Nə üçün? |
|------|----------|
| **launch_desktop.py** | Python launcher (background) |
| **start_vibeshield.bat** | Windows batch launcher |
| **desktop_app/run.bat** | Birbaşa UI başlatma |
| **desktop_app/main.py** | UI əsas fayl |
| **desktop_app/test_ui.py** | UI test skripti |
| **create_desktop_shortcut.ps1** | Desktop icon yaradır |

---

## ✅ Başlatma Uğurlu Oldu?

Əgər Desktop UI açıldısa:

- ✅ 8 tab görünür
- ✅ Pəncərə resize olunur
- ✅ Tab-lar arasında keçid işləyir
- ✅ Status bar altda "Hazır" göstərir

**Növbəti:** 🔑 API Keys tab-ında OpenRouter key əlavə edin!

---

## 🎉 Uğurlar!

Desktop app işləyir və istifadəyə hazırdır.

**Sualınız varsa:**
- FEATURES.md - Detallı xüsusiyyətlər
- SETUP_CHECKLIST.md - Quraşdırma
- QUICKSTART.md - 5 dəqiqəlik başlanğıc
