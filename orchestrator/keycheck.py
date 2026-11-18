"""
API açarlarının REAL canlı yoxlanışı.
Heç bir saxta (mock) cavab yoxdur: hər yoxlama real HTTP sorğusudur və
nəticədə serverin öz cavabı (status kodu + mesajı) qaytarılır.

- LLM: OpenAI-uyğun chat/completions ping (OpenRouter, OpenAI, Groq, lokal Ollama...)
- GitHub: api.github.com/user
"""

import json
import urllib.error
import urllib.request

from . import config

USER_AGENT = "VibeShield/2.0 (+desktop)"


def _post_json(url: str, headers: dict, payload: dict, timeout: int = 25):
    """POST + JSON cavab; (status, body_dict, err_mesaj) qaytarır."""
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={**headers, "Content-Type": "application/json", "User-Agent": USER_AGENT},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read().decode("utf-8", "replace")), None
    except urllib.error.HTTPError as e:
        try:
            body = json.loads(e.read().decode("utf-8", "replace"))
        except Exception:
            body = {}
        return e.code, body, _http_message(e.code, body)
    except urllib.error.URLError as e:
        return None, {}, f"Şəbəkə xətası: {e.reason}"
    except Exception as e:  # pragma: no cover
        return None, {}, f"{type(e).__name__}: {e}"


def _get_json(url: str, headers: dict, timeout: int = 20):
    req = urllib.request.Request(url, headers={**headers, "User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read().decode("utf-8", "replace")), dict(r.headers)
    except urllib.error.HTTPError as e:
        try:
            body = json.loads(e.read().decode("utf-8", "replace"))
        except Exception:
            body = {}
        return e.code, body, None
    except urllib.error.URLError as e:
        return None, {}, None
    except Exception:
        return None, {}, None


def _http_message(code: int, body: dict) -> str:
    msg = ""
    if isinstance(body, dict):
        err = body.get("error")
        if isinstance(err, dict):
            msg = str(err.get("message", ""))
        elif err:
            msg = str(err)
        msg = msg or str(body.get("message", ""))
    known = {401: "açar etibarsızdır (401 Unauthorized)",
             402: "balans/kredit bitib (402 Payment Required)",
             403: "giriş qadağandır (403)",
             404: "model və ya yol tapılmadı (404)",
             429: "limit aşıldı (429 rate limit)"}
    base = known.get(code, f"HTTP {code}")
    return f"{base} — {msg}" if msg else base


def check_llm(key: str, base: str, model: str) -> dict:
    """
    Real LLM bağlantı yoxlaması: 1 tokenlıq chat/completions ping.
    Qaytarır: {ok, detail, live, model}
      ok   — açar düzgündür və model cavab verdi
      live — real HTTP cavabı alındı (şəbəkə məsələsindən asılı deyil)
    """
    base = (base or "").rstrip("/")
    model = config.normalize_model(model) or "openai/gpt-4o-mini"
    if not base:
        return {"ok": False, "live": False, "detail": "API Base yazılmayıb", "model": model}

    headers = {}
    if key:
        headers["Authorization"] = f"Bearer {key}"
        headers["HTTP-Referer"] = "https://vibeshield.local"
        headers["X-Title"] = "VibeShield"

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "ping"}],
        "max_tokens": 1,
        "temperature": 0,
    }
    status, body, err = _post_json(f"{base}/chat/completions", headers, payload)
    live = status is not None
    if status == 200:
        choices = body.get("choices") or []
        used = body.get("model", model)
        return {"ok": True, "live": True, "detail": f"bağlantı OK — model cavab verdi ({used})", "model": used}
    if not live:
        return {"ok": False, "live": False, "detail": err or "server cavab vermədi", "model": model}
    return {"ok": False, "live": True, "detail": err or _http_message(status, body), "model": model}


def check_github(token: str) -> dict:
    """
    Real GitHub yoxlaması: GET /user.
    Qaytarır: {ok, live, detail} — detail-də login və scope-lar.
    """
    token = (token or "").strip()
    if not token:
        return {"ok": False, "live": False, "detail": "Token yazılmayıb"}
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    status, body, hdrs = _get_json("https://api.github.com/user", headers)
    live = status is not None
    if status == 200 and isinstance(body, dict) and body.get("login"):
        scopes = (hdrs or {}).get("X-OAuth-Scopes", "") or "heç bir scope"
        return {"ok": True, "live": True, "detail": f"bağlantı OK — GitHub istifadəçi: {body['login']} (scope: {scopes})"}
    if not live:
        return {"ok": False, "live": False, "detail": "api.github.com cavab vermədi — şəbəkə/timeout"}
    msg = ""
    if isinstance(body, dict):
        msg = str(body.get("message", ""))
    return {"ok": False, "live": True, "detail": msg or f"HTTP {status} — token etibarsızdır"}
