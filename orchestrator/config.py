"""
VibeShield konfiqurasiyası — repo kökü `config.json`.
Bütün API açarları BİR yerdə saxlanır; UI buradan yazır, engine buradan oxuyur.

Prioritet hər yerdə eynidir:  mühit dəyişəni  →  config.json  →  boş.
config.json .gitignore-dadır — açarlar repoya düşmür.
"""

import json
import os
import threading
from pathlib import Path

from .resolver import REPO_ROOT

CONFIG_PATH = REPO_ROOT / "config.json"

# Xəritə: mühit dəyişəni → config.json açarı
ENV_TO_CONFIG = {
    "LLM_API_KEY": "llm_api_key",     # OpenRouter / OpenAI / Groq / ... (OpenAI-uyğun)
    "LLM_API_BASE": "llm_api_base",   # https://openrouter.ai/api/v1
    "STRIX_LLM": "strix_llm",         # model adı: openai/gpt-4o-mini
    "GITHUB_TOKEN": "github_token",   # api.github.com üçün PAT
}

DEFAULTS = {
    "llm_api_base": "https://openrouter.ai/api/v1",
    "strix_llm": "openai/gpt-4o-mini",
}

_lock = threading.Lock()


def load_config() -> dict:
    """config.json oxu (yanlış JSON → boş dict, heç vaxt crash etmir)."""
    with _lock:
        if CONFIG_PATH.is_file():
            try:
                return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            except Exception:
                return {}
    return {}


def save_config(patch: dict) -> dict:
    """config.json-a yamaq (merge) yaz — mövcud açarlar itmir."""
    with _lock:
        cfg = {}
        if CONFIG_PATH.is_file():
            try:
                cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            except Exception:
                cfg = {}
        cfg.update(patch)
        CONFIG_PATH.write_text(json.dumps(cfg, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return cfg


def delete_keys(config_names) -> dict:
    """Göstərilən config sahələrini sil (Settings 'Təmizlə')."""
    names = set(config_names)
    with _lock:
        cfg = {}
        if CONFIG_PATH.is_file():
            try:
                cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            except Exception:
                cfg = {}
        for n in names:
            cfg.pop(n, None)
        CONFIG_PATH.write_text(json.dumps(cfg, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return cfg


def get_value(env_name: str) -> str:
    """Açarın real dəyəri: mühit → config.json → boş sətir."""
    v = os.environ.get(env_name, "").strip()
    if v:
        return v
    cfg_name = ENV_TO_CONFIG.get(env_name, "")
    if cfg_name:
        return str(load_config().get(cfg_name, "")).strip()
    return ""


def get_default(env_name: str) -> str:
    """get_value + DEFAULTS ilə geri düşmə (base/model kimi sahələr üçün)."""
    v = get_value(env_name)
    if v:
        return v
    cfg_name = ENV_TO_CONFIG.get(env_name, "")
    return DEFAULTS.get(cfg_name, "")


def normalize_model(model: str) -> str:
    """Strix üslubundakı 'openrouter/...' prefiksini təmizlə — birbaşa API model ID-si üçün."""
    m = (model or "").strip()
    return m[len("openrouter/"):] if m.startswith("openrouter/") else m


def mask(secret: str) -> str:
    """Açarı UI üçün maskala — tam dəyər heç vaxt göstərilmir."""
    if not secret:
        return ""
    if len(secret) <= 10:
        return secret[:2] + "…" + "•" * 6
    return secret[:7] + "…" + secret[-4:]


def status_line() -> str:
    """Bütün açarların cari vəziyyəti (Settings başlığı üçün)."""
    parts = []
    for env_name in ("LLM_API_KEY", "GITHUB_TOKEN"):
        v = get_value(env_name)
        src = "env" if os.environ.get(env_name, "").strip() else "config"
        parts.append(f"{env_name}: {'✓ ' + mask(v) if v else '✗ yoxdur'} ({src})")
    return " | ".join(parts)
