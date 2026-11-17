"""QA: Audit Rules — 13 qaydanın real deteksiyası."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from audit.rules import AuditEngine, RULES  # noqa: E402


def _scan(text: str):
    engine = AuditEngine()
    return engine.scan_file_text(text) if hasattr(engine, "scan_file_text") else engine.scan_content(text)


def test_rule_count():
    assert len(RULES) == 13


def test_hardcoded_api_key_detected():
    engine = AuditEngine()
    f = engine.scan_content("const API_KEY = 'sk_test_abcdefgh1234567890'")
    assert any(r["rule_id"] == "VS-001" for r in f)


def test_eval_detected():
    engine = AuditEngine()
    f = engine.scan_content("eval(userInput)")
    assert any(r["rule_id"] == "VS-009" for r in f)


def test_weak_crypto_detected():
    engine = AuditEngine()
    f = engine.scan_content("const h = md5(password)")
    assert any(r["rule_id"] == "VS-005" for r in f)


def test_cors_wildcard_detected():
    engine = AuditEngine()
    f = engine.scan_content('res.header("Access-Control-Allow-Origin", "*")')
    assert any(r["rule_id"] == "VS-011" for r in f)


def test_hardcoded_password_detected():
    engine = AuditEngine()
    f = engine.scan_content('const password = "hunter2secret"')
    assert any(r["rule_id"] == "VS-012" for r in f)


def test_clean_code_no_findings():
    engine = AuditEngine()
    f = engine.scan_content("const greeting = 'hello world'\nconsole.log(greeting)")
    # Math.random yox, eval yox, secret yox
    assert not [r for r in f if r["rule_id"] in ("VS-001", "VS-009", "VS-012")]


def test_clean_code_zero_findings():
    engine = AuditEngine()
    f = engine.scan_content("const a = 1;\nconst b = 2;\n")
    assert f == []
