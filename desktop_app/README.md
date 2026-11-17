# DevSecOps Desktop Tool

Masaüstü tətbiqi — 7-addımlı deterministik DevSecOps pipeline-i local olaraq idarə etmək üçün.

## Qurulma

```
ssimi/
└── desktop_app/
    ├── main.py           # Tkinter GUI
    ├── scanner.py        # Strix, Nuclei, Semgrep, Trivy, Gitleaks
    ├── gate.py           # Deterministik qapı (jq+JSON ekvivalent)
    ├── config.json       # Konfiqurasiya (OpenRouter açarı, model, hedef)
    ├── requirements.txt  # Python kitabxanaları
    └── run.bat           # Windows işlədirmə skripti
```

## Tələblər

- Python 3.9+ (Tkinter daxil olmaqla)
- İstəyə bağlı CLI alətləri:
  - `strix` — `curl -sSL https://strix.ai/install | bash`
  - `nuclei` — https://github.com/projectdiscovery/nuclei
  - `semgrep` — `pip install semgrep`
  - `trivy` — https://github.com/aquasecurity/trivy
  - `gitleaks` — https://github.com/gitleaks/gitleaks

## İşlətmə

### Windows
```bash
cd desktop_app
run.bat
```

### Cross-platform
```bash
cd desktop_app
pip install -r requirements.txt
python main.py
```

## Sekmələr

| Sekme | Təsərrüfatı |
|-------|-------------|
| **⚙️ Konfiqurasiya** | OpenRouter API açarı, model, hedef URL, aktiv alətlər, qapı səviyyəsi |
| **🔍 Skanlar** | Bütün aktive skanları işləyir, nəticələri cədvəlündə göstərir |
| **🚪 Deterministik Qapı** | `unified_findings.json` yaradır, `jq` ekvivalent}qapı qərarını düşürür |
| **📄 Hesabat** | `report.pdf` və `unified_findings.json` görüntüləməsi |
| **📋 Loglar** | Tətbiqi icra logları |

## Deterministik Qapı (Addım 6)

Qərar yalnız `unified_findings.json` dən oxunur. LLM (Strix/OpenRouter) bu qərara müdaxilə etmir.

- Kritik və ya ↑zəiflik sayısı > 0 → **PUBLISH BLOKLANDI**
- Say = 0 → **PUBLISH-Ə İCAZƏ VERİLİR**

## OpenRouter konfiqurasiyası

1. [openrouter.ai](https://openrouter.ai)-də hesab yaratın
2. API açarı alın (`sk-or-...`)
3. Masaüstü tool-un **⚙️ Konfiqurasiya** sekmesində açarı daxil edin
4. Model seçin: `openrouter/google/gemma-2-9b-it` (pulsuz tier)
5. Hedef URL: `http://localhost:8000` (sandbox target_app)

## Loop

- **Loop 1:** Strix zəiflik taparsa → auto-fix PR → merge → yenidən push → qapı
- **Loop 2:** Kod keyfiyyəti aşağıdırsa → Strix-ə çatılmaz → düzəld → yenidən push

Bu tool 100% pulsuzdur, Jenkins tələb etmir.