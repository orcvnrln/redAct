# VibeShield Orchestrator — Tam Avtonom DevSecOps/QA/Pentest

`orchestrator/` modulu layihənin özəyidir: 6 security tool-u bir işə salır,
nəticələri **vahid formata** gətirir, **deterministik gate** qərarı verir və
hesabat yaradır. LLM qərar işinə qarışmır — qərar yalnız JSON-dan gəlir.

## Tool statusu (real)

| Tool | Tip | Status | Mənbə |
|------|-----|--------|-------|
| Audit Engine | SAST | ✅ Active | repo daxili (`audit/`) |
| Semgrep | SAST | ✅ Active | pip (`strix-agent` ilə venv) |
| Gitleaks | Secrets | ✅ Active | `tools/bin/gitleaks` (GitHub release) |
| Trivy | SCA+Secrets+IaC | ✅ Active | `tools/bin/trivy` (GitHub release) |
| Nuclei | DAST | ✅ Active | `tools/bin/nuclei` + 87MB template |
| Strix | AI Pentest | ⚙️ şərti | `pip install strix-agent`; Docker + `LLM_API_KEY` tələb edir, yoxdursa SKIPPED |

## Quraşdırma (avtonom)

```bash
bash tools/install.sh          # ən son versiyaları GitHub-dan özü çəkir
python -m orchestrator.cli doctor   # mühit yoxlaması
```

## İşə salma

```bash
source .venv/bin/activate
export PATH="$PWD/tools/bin:$PATH"

# 1) Tam pipeline: statik + secrets + SCA + canlı DAST
node target_app/server.js &                        # hədəf (varsa)
python -m orchestrator.cli run \
    --project ./target_app \
    --target http://localhost:8000 \
    --profile full

# 2) Sürətli profil (audit + gitleaks)
python -m orchestrator.cli run --project ./myapp --profile fast

# 3) Yalnız QA (audit + semgrep)
python -m orchestrator.cli run --project ./myapp --profile qa

# 4) Yalnız pentest (nuclei + strix, hədəf mütləq)
python -m orchestrator.cli run --target http://localhost:8000 --profile pentest
```

Çıxış kodu: `0` = gate KEÇDİ, `1` = gate BLOKLANDI, `2` = konfiqurasiya xətası.
CI/CD-də birbaşa işlədilir.

## Profillər

| Profil | Tool-lar | Gate | Tələb |
|---------|----------|------|-------|
| `full` | hamısı 6 | critical+high | `--target` mütləq |
| `fast` | audit_engine, gitleaks | critical+high | — |
| `qa` | audit_engine, semgrep | critical | — |
| `pentest` | nuclei, strix | critical+high | `--target` mütləq |

## Çıxış faylları (`scan_out/<project>/`)

- `unified_findings.json` — bütün tapıntılar vahid şemada (tool, severity, cwe, yer)
- `report.md` — insan üçün tam hesabat
- `semgrep.json`, `gitleaks.json`, `trivy.json`, `nuclei.jsonl` — raw tool çıxışları
- `strix_runs/<run>/vulnerabilities.json` — Strix öz nəticələrini buraya yazır (`--output` parametri strix CLI-də yoxdur)

## Arxitektura

```
orchestrator/
├── cli.py          # run / tools / doctor
├── engine.py       # pipeline, profillər, hədəf gözləmə, paralel skan
├── tools/__init__.py  # 6 tool runner (subprocess + real status)
├── unified.py      # normalizasiya + dedup + severity sıralama
├── gate.py         # deterministik gate (LLM-siz)
├── report.py       # unified JSON + markdown hesabat
├── runner.py       # subprocess: timeout, retry, NOT_FOUND crashey etmir
└── resolver.py     # tool axtarışı: tools/bin → ~/.vibeshield → PATH
```

## QA

```bash
python -m pytest tests/ -q      # 27 test: rules, gate, unified, pipeline
```

## Avtonom prinsiplər

1. **Saxta nəticə yoxdur** — tool yoxdursa `SKIPPED` + səbəb, xəta varsa `FAILED` + exit kodu.
2. **Özünü skan etmir** — çıxış faylları proyektin xaricində tutulur (`scan_out/`).
3. **Determinizm** — gate qərarı yalnız severity sayından gəlir; Strix nəticəsi xüsusilə işarələnir.
4. **Paralellik** — bütün tool-lar eyni anda işləyir; biri çöksə, digərləri davam edir.
5. **Exit-kod intizamı** — CI üçün: 0 keç, 1 blok, 2 setup xətası.
