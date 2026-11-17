# VibeShield — Sistem Arxitekturası

## Ümumiləşdirilmiş Qat Diaqramı

```
┌─────────────────────────────────────────────────────────────────┐
│                        DEVELOPER PUSH                            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  ADDIM 1: BUILD + UNIT TEST                                      │
│  ├─ npm ci && npm test --ci                                      │
│  └─ Exit 0 → davam, Exit 1 → DAYAN                             │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  ADDIM 2: STATIK YOXLAMA (Paralel)                              │
│  ┌───────────┬───────────┬───────────┐                          │
│  │ Gitleaks  │ Semgrep   │  Trivy    │                          │
│  │ (secrets) │ (SAST)    │  (SCA)    │                          │
│  └─────┬─────┴─────┬─────┴─────┬─────┘                          │
│        │           │           │                                 │
│        └───────────┴───────────┴──────► *.json                  │
│  continue-on-error: true (bloklamır)                            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  ADDIM 2.5: AUDIT ENGINE (Deterministik)                        │
│  ├─ 13 regex qayda                                              │
│  ├─ Python əsaslı                                               │
│  ├─ LLM yoxdur                                                  │
│  └─ Exit 1 əgər critical/high > 0 → DAYAN                       │
│     audit_findings.json                                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  ADDIM 3: SANDBOX DEPLOY                                         │
│  ├─ docker compose -f docker-compose.sandbox.yml up -d          │
│  ├─ Healthcheck: curl http://target_app:8000/health            │
│  └─ internal: true (xarici şəbəkə çıxışı YOXDUR)               │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  ADDIM 4: AI PENTEST (Strix)                                    │
│  ├─ strix -n --target http://target_app:8000                   │
│  ├─ --config strix-config.yaml                                 │
│  ├─ LLM: OpenRouter/Gemma-2-9B-IT (pulsuz)                     │
│  ├─ --fail-on high                                             │
│  └─ Exit 2 əgər zəiflik → Addım 5-ə keç                        │
│     Exit 0 → Addım 6-ya keç                                     │
│     findings.json                                                │
└────────────────────────────┬────────────────────────────────────┘
                             │
                    ┌────────┴────────┐
                    │                 │
              Exit 2 (zəiflik)  Exit 0 (təmiz)
                    │                 │
                    ▼                 │
┌─────────────────────────────────┐  │
│  ADDIM 5: AI AUTO-FIX           │  │
│  ├─ Yalnız Strix uğursuz olarsa│  │
│  ├─ Kavach AI                   │  │
│  └─ PR açır → loop              │  │
└─────────────────────────────────┘  │
                    │                 │
                    └────────┬────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  ADDIM 6: DETERMİNİSTİK QAPI (LLM-siz)                          │
│  ┌───────────────────────────────────────────────────┐          │
│  │  jq -s 'map(select(. != null)) | add' \          │          │
│  │    semgrep.json trivy.json findings.json \       │          │
│  │    audit_findings.json > unified_findings.json   │          │
│  │                                                   │          │
│  │  CRITICAL=$(jq '[.findings[]? |                  │          │
│  │    select(.severity=="critical" or               │          │
│  │            .severity=="high")] | length')        │          │
│  │                                                   │          │
│  │  if [ "$CRITICAL" -gt 0 ]; then                 │          │
│  │    exit 1  # 🚫 BLOK                            │          │
│  │  else                                            │          │
│  │    exit 0  # ✅ KEÇ                             │          │
│  │  fi                                              │          │
│  └───────────────────────────────────────────────────┘          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                    ┌────────┴────────┐
                    │                 │
              Exit 1 (blok)     Exit 0 (keç)
                    │                 │
                    ▼                 ▼
        ┌───────────────────┐ ┌──────────────────┐
        │  PUBLISH BLOK      │ │  ADDIM 7: REPORT │
        │  Deploy təxirə     │ │  ├─ devsecops-   │
        │  salınır           │ │  │  radar         │
        │                    │ │  ├─ report.pdf   │
        │                    │ │  └─ artifact     │
        └───────────────────┘ └──────────┬────────┘
                                         │
                                         ▼
                              ┌──────────────────┐
                              │  PUBLISH / DEPLOY│
                              │  ✅ Qapı keçdi   │
                              └──────────────────┘
```

## Komponent Əlaqələri

```
┌────────────────────────────────────────────────────────────────┐
│                                                                 │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐ │
│  │   AUDIT      │◄─────┤  DESKTOP_APP │─────►│  GATE.PY     │ │
│  │   ENGINE     │      │  (UI)        │      │  (DECISION)  │ │
│  │  (13 rules)  │      └──────────────┘      └──────────────┘ │
│  └──────┬───────┘                                   ▲          │
│         │                                           │          │
│         │ audit_findings.json                       │          │
│         ▼                                           │          │
│  ┌──────────────────────────────────────────────────┴────────┐ │
│  │          UNIFIED_FINDINGS.JSON                            │ │
│  │  (semgrep + trivy + strix + audit)                        │ │
│  └───────────────────────────────────────────────────────────┘ │
│         ▲              ▲              ▲                         │
│         │              │              │                         │
│  ┌──────┴──────┐ ┌────┴─────┐ ┌─────┴──────┐                  │
│  │  Semgrep    │ │  Trivy   │ │  Strix AI  │                  │
│  │  (SAST)     │ │  (SCA)   │ │  (DAST)    │                  │
│  └─────────────┘ └──────────┘ └────────────┘                  │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

## Data Flow (Məlumat Axını)

```
1. DEVELOPER
   │
   ├─► git push
   │
   └─► GitHub Actions trigger
       │
       ├─► Build + Test ────────────────► Exit 0/1
       │
       ├─► Gitleaks ──────────────────────► secrets.json
       ├─► Semgrep ───────────────────────► semgrep.json
       ├─► Trivy ─────────────────────────► trivy.json
       ├─► Audit Engine ──────────────────► audit_findings.json
       │                                        │
       │                                        │ Exit 1?
       │                                        ▼
       │                                   STOP (critical/high)
       │
       ├─► Docker Compose ─────────────────► Sandbox up
       │                                        │
       │                                        ▼
       ├─► Strix AI ──────────────────────► findings.json
       │                                        │
       │                                   Exit 2? ──► Kavach AI ──► PR
       │                                        │
       │                                   Exit 0
       │                                        │
       └─► jq merge ───────────────────────► unified_findings.json
                                                │
                                                ├─► CRITICAL=$(jq '[...] | length')
                                                │
                                                ├─► if CRITICAL > 0
                                                │   ├─► exit 1 (BLOK)
                                                │   └─► Publish skipt olur
                                                │
                                                └─► if CRITICAL == 0
                                                    ├─► exit 0 (KEÇ)
                                                    ├─► Report
                                                    └─► Publish
```

## Sandbox Təhlükəsizliyi

```
┌─────────────────────────────────────────────────────────────┐
│  DOCKER SANDBOX (internal: true)                            │
│                                                              │
│  ┌────────────────────────────┐  ┌──────────────────────┐  │
│  │  target_app                │  │  attacker (Strix)    │  │
│  │  ├─ Port: 8000             │◄─┤  ├─ HTTP sorğular   │  │
│  │  ├─ read_only: true        │  │  ├─ PoC test        │  │
│  │  ├─ cap_drop: ALL          │  │  └─ findings.json   │  │
│  │  ├─ user: 10001            │  │     yaradır          │  │
│  │  └─ no-new-privileges      │  └──────────────────────┘  │
│  └────────────────────────────┘                             │
│                                                              │
│  Network: sandbox_net                                        │
│  ├─ internal: true  ◄───── XARİCİ ŞƏBƏKƏyə ÇIXIŞ YOXDUR   │
│  └─ subnet: 172.30.0.0/24                                   │
│                                                              │
│  ❌ Bloklanmış:                                             │
│     ├─ İnternet çıxışı                                      │
│     ├─ Host fayl sisteminə çatış                           │
│     ├─ Privilege escalation                                 │
│     └─ Konteyner breakout                                   │
└─────────────────────────────────────────────────────────────┘
```

## Deterministik Qapı Alqoritmi

```python
def evaluate_gate(unified_findings_path: str) -> Tuple[bool, int]:
    """
    LLM-siz deterministik qərar
    """
    data = json.load(open(unified_findings_path))
    findings = data.get("findings", [])
    
    critical_count = 0
    for finding in findings:
        severity = finding.get("severity", "").lower()
        if severity in ["critical", "high"]:
            critical_count += 1
    
    # Qərar yalnız saydan asılıdır
    passed = critical_count == 0
    
    return passed, critical_count

# İstifadə
passed, count = evaluate_gate("unified_findings.json")
if not passed:
    print(f"🚫 BLOK: {count} critical/high tapıntı")
    exit(1)
else:
    print("✅ KEÇ: zəiflik yoxdur")
    exit(0)
```

## Audit Engine Qayda Strukturu

```python
class AuditRule:
    rule_id: str        # VS-001, VS-002, ...
    name: str           # Qayda adı
    severity: str       # critical, high, medium, low
    pattern: re.Pattern # Regex pattern
    description: str    # Açıqlama
    cwe: str           # CWE-798, CWE-89, ...
    owasp: str         # A01:2021, A02:2021, ...
    
    def check(content: str, file_path: str) -> List[Finding]:
        """
        Faylda pattern axtarır, tapıntılar qaytarır
        """
        findings = []
        for match in self.pattern.finditer(content):
            line_num = content[:match.start()].count('\n') + 1
            findings.append({
                "rule_id": self.rule_id,
                "severity": self.severity,
                "file": file_path,
                "line": line_num,
                "match": match.group(0)[:100],
                "cwe": self.cwe,
                "owasp": self.owasp,
            })
        return findings
```

## Strix İnteqrasiyası

```yaml
# strix-config.yaml
llm:
  provider: openrouter
  model: openrouter/google/gemma-2-9b-it
  temperature: 0  # deterministik davranış üçün

scan:
  target: http://target_app:8000
  mode: quick
  fail_on: high  # exit 2 əgər high/critical
  
  instruction: |
    Focus ONLY on IDOR, auth bypass, secret exposure.
    Test auth matrix: no token, user A, user B.
    Report ONLY PoC-validated findings.

auth_matrix:
  - no_token
  - user_a
  - user_b

endpoints:
  - /api/users/1
  - /api/profile/1
  - /api/debug/env
```

## Xəta Halları və Fallback

```
Strix uğursuz (LLM cavab vermir)
    │
    ├─► Nuclei fallback işləyir
    │   └─► nuclei.json yaradır
    │
    └─► Əgər Nuclei də uğursuzsa
        └─► Yalnız statik nəticələr istifadə olunur
            (Semgrep + Trivy + Audit)
```

## Performans Metrikaları

| Qat | Alət | Ortalama Müddət | Blok Edə Bilər? |
|-----|------|-----------------|------------------|
| Statik | Gitleaks | 10-20s | Xeyr (continue-on-error) |
| Statik | Semgrep | 30-60s | Xeyr (continue-on-error) |
| Statik | Trivy | 20-40s | Xeyr (continue-on-error) |
| **Statik** | **Audit** | **5-15s** | **Bəli (exit 1)** |
| Deploy | Docker | 20-30s | Bəli (healthcheck) |
| **Dinamik** | **Strix** | **3-7 dəq** | **Bəli (exit 2)** |
| Fix | Kavach | 1-2 dəq | Xeyr (PR yaradır) |
| **Qapı** | **jq** | **<1s** | **Bəli (exit 1)** |
| Hesabat | devsecops-radar | 30-60s | Xeyr |

**Ümumi:** ~5-15 dəqiqə (LLM ilə), ~3-5 dəqiqə (yalnız statik)

## Əlaqə Diaqramı

```
Developer ───► GitHub ───► Actions ───► Audit ───► Sandbox ───► Strix
                                            │           │          │
                                            ▼           ▼          ▼
                                        findings    findings   findings
                                            │           │          │
                                            └───────────┴──────────┘
                                                       │
                                                       ▼
                                              unified_findings.json
                                                       │
                                                       ▼
                                                Gate (jq)
                                                       │
                                              ┌────────┴────────┐
                                              │                 │
                                         BLOK (exit 1)    KEÇ (exit 0)
                                              │                 │
                                              ▼                 ▼
                                         Stop workflow    Publish
```

## Təhlükəsizlik Qatları

1. **Pre-commit** — Gitleaks (lokal)
2. **Build** — Unit testlər
3. **Statik** — Gitleaks + Semgrep + Trivy + Audit
4. **Dinamik** — Strix (sandbox daxilində)
5. **Qapı** — Deterministik qərar (jq)
6. **Fix** — AI auto-fix (loop)
7. **Monitor** — Report + artifact

Hər qat uğursuz olarsa, növbəti qat işləmir (fail-fast). Bu, resurs qənaəti və sürət deməkdir.
