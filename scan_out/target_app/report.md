# 🛡️ VibeShield — Tam Avtonom DevSecOps Hesabatı

**Tarix:** 2026-11-17T21:39:43.429891  
**Proyekt:** `/home/main/redact/redAct/target_app`  
**Live hədəf:** `yoxdur (yalnız statik)`  
**Profil:** `fast`

## 🔀 Gate Qərarı (deterministik, LLM-siz)

## ❌ BLOKLANDI — 3 ['critical', 'high'] severity tapıntı — deploy bloklandı

| Severity | Say |
|---|---|
| critical | 1 |
| high | 2 |
| medium | 0 |
| low | 0 |
| info | 0 |

## 🧰 Tool Statusları

| Tool | Status | Tapıntı | Müddət | Qeyd |
|---|---|---|---|---|
| audit_engine | ✅ OK | 2 | 0.09s | — |
| gitleaks | ✅ OK | 1 | 0.94s | — |

## 🚨 Tapıntılar (critical→info sıralı)

### 1. [CRITICAL] Hardcoded API Key  (audit_engine)
- **Yer:** `/home/main/redact/redAct/target_app/server.js:8`
- **CWE/OWASP:** CWE-798 / A02:2021
- **Təsvir:** API key hardcoded olunub - secret management istifadə edin

### 2. [HIGH] Debug/Admin Endpoint  (audit_engine)
- **Yer:** `/home/main/redact/redAct/target_app/server.js:37`
- **CWE/OWASP:** CWE-489 / A05:2021
- **Təsvir:** Debug/admin endpoint production-da açıq qala bilər

### 3. [HIGH] Found a Stripe Access Token, posing a risk to payment processing services and sensitive financial data.  (gitleaks)
- **Yer:** `/home/main/redact/redAct/target_app/server.js:8`
- **CWE/OWASP:** CWE-798 / A02:2021
- **Təsvir:** Secret: REDACTED…


## 📎 Fayllar

- `unified_findings.json` — hamıdan vahid formatda
- `audit_findings.json` — audit_engine raw nəticə
- `gitleaks.json` — gitleaks raw nəticə