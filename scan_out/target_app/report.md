# 🛡️ VibeShield — Tam Avtonom DevSecOps Hesabatı

**Tarix:** 2026-11-17T21:12:56.007213  
**Proyekt:** `/home/main/redact/redAct/target_app`  
**Live hədəf:** `http://localhost:8000`  
**Profil:** `full`

## 🔀 Gate Qərarı (deterministik, LLM-siz)

## ❌ BLOKLANDI — 4 ['critical', 'high'] severity tapıntı — deploy bloklandı

| Severity | Say |
|---|---|
| critical | 1 |
| high | 3 |
| medium | 1 |
| low | 1 |
| info | 3 |

## 🧰 Tool Statusları

| Tool | Status | Tapıntı | Müddət | Qeyd |
|---|---|---|---|---|
| audit_engine | ✅ OK | 2 | 0.14s | — |
| semgrep | ✅ OK | 1 | 14.92s | — |
| gitleaks | ✅ OK | 1 | 2.05s | — |
| trivy | ✅ OK | 2 | 3.81s | — |
| nuclei | ✅ OK | 10 | 152.04s | — |
| strix | ⏭️ SKIPPED | 0 | 0.0s | LLM_API_KEY yoxdur (strix AI agent üçün açar tələb edir) |

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

### 4. [HIGH] Stripe Secret Key  (trivy)
- **Yer:** `server.js:8`
- **CWE/OWASP:** CWE-798 / —
- **Təsvir:** Secret tapıldı (const API_SECRET = '********************)

### 5. [MEDIUM] Node.js Express NODE_ENV Development Mode  (nuclei)
- **Yer:** `http://localhost:8000`
- **CWE/OWASP:** cwe-209 / —
- **Təsvir:** The Node.js application runs in development mode, which can expose sensitive information, such as source code and secrets, depending on the application.


### 6. [LOW] DS-0026: No HEALTHCHECK defined  (trivy)
- **Yer:** `Dockerfile:0`
- **CWE/OWASP:** — / —
- **Təsvir:** You should add HEALTHCHECK instruction in your docker container images to perform the health check on running containers.

### 7. [INFO] javascript.express.security.audit.express-check-csurf-middleware-usage.express-check-csurf-middleware-usage  (semgrep)
- **Yer:** `/home/main/redact/redAct/target_app/server.js:2`
- **CWE/OWASP:** ['CWE-352: Cross-Site Request Forgery (CSRF)'] / ['A01:2021 - Broken Access Control', 'A01:2025 - Broken Access Control']
- **Təsvir:** A CSRF middleware was not detected in your express application. Ensure you are either using one such as `csurf` or `csrf` (see rule references) and/or you are properly doing CSRF validation in your routes with a token or cookies.

### 8. [INFO] Wappalyzer Technology Detection  (nuclei)
- **Yer:** `http://localhost:8000`
- **CWE/OWASP:** — / —
- **Təsvir:** —

### 9. [INFO] HTTP Missing Security Headers  (nuclei)
- **Yer:** `http://localhost:8000`
- **CWE/OWASP:** cwe-693 / —
- **Təsvir:** This template searches for missing HTTP security headers. The impact of these missing headers can vary.



## 📎 Fayllar

- `unified_findings.json` — hamıdan vahid formatda
- `audit_findings.json` — audit_engine raw nəticə
- `semgrep.json` — semgrep raw nəticə
- `gitleaks.json` — gitleaks raw nəticə
- `trivy.json` — trivy raw nəticə
- `nuclei.jsonl` — nuclei raw nəticə
- `strix.json` — strix raw nəticə