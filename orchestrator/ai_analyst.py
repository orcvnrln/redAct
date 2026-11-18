"""
AI Təhlükəsizlik Analitiki — tapıntıları REAL LLM API-nə göndərir.
OpenRouter / OpenAI / Groq / lokal Ollama — hamısı OpenAI-uyğun chat/completions ilə.

Mock/saxta cavab YOXDUR: API açarı yoxdursa və ya server cavab vermirsə
AIError qalxır və UI-də real xəta göstərilir.
"""

import json
import urllib.error
import urllib.request

from .config import get_value, get_default, normalize_model
from .keycheck import USER_AGENT

SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}


class AIError(Exception):
    """Real API xətası — UI bunu istifadəçiyə göstərir."""


SYSTEM_PROMPT = (
    "Sən təcrübəli bir kibertəhlükəsizlik və DevSecOps analitikisən. "
    "Sənə DevSecOps pipeline-ının deduplanmış tapıntıları (SAST, secrets, dependency, DAST) verilir. "
    "Cavabı AZƏRBAYCAN dilində, qısa, konkret və işə yarar yaz. Struktur:\n"
    "1) CRITICAL/HAZARD — ən təhlükəli 3-5 tapıntı və niyə təhlükəlidir (bir sətir hər biri).\n"
    "2) Kök səbəb — kod bazasında dəfələrlə görülən sistemlik səhvlər.\n"
    "3) Düzəliş planı — konkret addımlar (koddan istifadə örnek sətri ilə).\n"
    "4) Gate qərarı — bu tapıntılarla deploy bloklanmalıdırmı, 1 sətir.\n"
    "Qısa ol: boş danışma, tapıntıya bağlanmayan ümumi söz yazma."
)


def _api_key() -> str:
    return get_value("LLM_API_KEY")


def _api_base() -> str:
    return get_default("LLM_API_BASE")


def _model() -> str:
    return normalize_model(get_default("STRIX_LLM"))


def _headers(key: str) -> dict:
    h = {"Content-Type": "application/json", "User-Agent": USER_AGENT,
         "HTTP-Referer": "https://vibeshield.local", "X-Title": "VibeShield"}
    if key:
        h["Authorization"] = f"Bearer {key}"
    return h


def _chat(messages, model: str, max_tokens: int = 1600, timeout: int = 90) -> str:
    """Bir chat/completions sorğusu — REAL. Xəta → AIError (real mesajla)."""
    base = _api_base().rstrip("/")
    key = _api_key()
    if not base:
        raise AIError("API Base təyin edilməyib (Settings → LLM).")
    payload = {"model": model, "messages": messages, "max_tokens": max_tokens, "temperature": 0.2}
    req = urllib.request.Request(
        f"{base}/chat/completions",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers=_headers(key), method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = json.loads(r.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as e:
        try:
            err = json.loads(e.read().decode("utf-8", "replace"))
            msg = err.get("error", {}).get("message", "") if isinstance(err, dict) else str(err)
        except Exception:
            msg = ""
        known = {401: "API açarı etibarsızdır", 402: "balans bitib", 403: "giriş qadağandır",
                 404: "model tapılmadı", 429: "limit aşıldı"}
        base_msg = known.get(e.code, f"HTTP {e.code}")
        raise AIError(f"{base_msg}{' — ' + msg if msg else ''}")
    except urllib.error.URLError as e:
        raise AIError(f"Şəbəkə xətası: {e.reason} — API-ya çatıla bilmədi")
    except Exception as e:  # pragma: no cover
        raise AIError(f"{type(e).__name__}: {e}")

    choices = body.get("choices") or []
    if not choices:
        raise AIError(f"API cavabı boş (choices yoxdur): {json.dumps(body, ensure_ascii=False)[:200]}")
    content = (choices[0].get("message") or {}).get("content") or ""
    if not content:
        raise AIError("API cavabı boş mətn qaytardı.")
    return content


def connection_test(model: str = "") -> str:
    """Settings 'Test' düyməsi üçün: real ping. Cavab: insan oxumalı mətn."""
    key = _api_key()
    base = _api_base().rstrip("/")
    if not base:
        raise AIError("API Base təyin edilməyib.")
    if not key:
        raise AIError("API açarı yoxdur — Settings-də əlavə et.")
    # Reasoning modellər (məs. nemotron) token-ləri əvvəlcə "reasoning"-ə xərcləyir,
    # ona görə max_tokens=1 boş content qaytarır. 64 balanslıdır.
    out = _chat([{"role": "user", "content": "ping"}], model=model or _model(),
                max_tokens=64, timeout=45)
    used = model or _model()
    return f"✅ Bağlantı REAL işləyir — {used} cavab verdi ({base}): {out.strip()[:40]}"


def analyze_findings(findings: list, model: str = "", max_findings: int = 45) -> str:
    """
    Tapıntıları real LLM ilə təhlil edir, mətn qaytarır.
    Key yoxdursa AIError: 'API açarı yoxdur' — mock cavab heç vaxt yoxdur.
    """
    key = _api_key()
    if not key:
        raise AIError("API açarı yoxdur — Settings-də LLM API Key əlavə et, sonra yenidən sınayın.")
    model = model or _model()

    rows = sorted(findings, key=lambda f: SEVERITY_ORDER.get(str(f.get("severity", "info")).lower(), 5))[:max_findings]
    compact = [
        {
            "sev": f.get("severity"),
            "tool": f.get("tool"),
            "title": (f.get("title") or "")[:120],
            "where": f.get("url") or ((str(f.get("file") or "") + (":" + str(f["line"]) if f.get("line") else "")) or "—"),
            "rule": f.get("rule_id") or "",
        }
        for f in rows
    ]
    if not compact:
        return "Tapıntı yoxdur — analiz üçün əvvəlcə bir run keçirin."

    user = (
        "Bu VibeShield pipeline tapıntılarıdır (JSON). Təhlil et:\n\n"
        + json.dumps({"total": len(findings), "shown": len(compact), "findings": compact},
                     ensure_ascii=False)
    )
    return _chat(
        [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user}],
        model=model,
    )
