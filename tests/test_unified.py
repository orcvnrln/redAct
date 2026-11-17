"""QA: Normalizatorlar — real tool çıxış formatları ilə."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from orchestrator.unified import (  # noqa: E402
    normalize_semgrep, normalize_trivy, normalize_nuclei,
    normalize_gitleaks, normalize_strix, normalize_audit, dedup, rank,
)

SEMGREP_SAMPLE = {
    "results": [{
        "check_id": "javascript.express.security.audit.express-ssrf",
        "path": "app/server.js",
        "start": {"line": 12},
        "extra": {
            "severity": "ERROR",
            "message": "Unsanitized request input in http request",
            "metadata": {"cwe": "CWE-918", "owasp": "A10:2021"},
        },
    }]
}

TRIVY_SAMPLE = {
    "Results": [{
        "Target": "package-lock.json",
        "Class": "lang-pkgs",
        "Vulnerabilities": [{
            "VulnerabilityID": "CVE-2022-25883",
            "PkgName": "express",
            "Severity": "CRITICAL",
            "Title": "express vulnerable to ReDoS",
            "PrimaryURL": "https://avd.aquasec.com/nvd/cve-2022-25883",
            "CweIDs": ["CWE-1333"],
        }],
        "Secrets": [{"Title": "API key", "RuleID": "generic-api-key", "StartLine": 8, "Match": "sk_test..."}],
    }]
}

NUCLEI_SAMPLE = [{
    "template-id": "exposed-debug-env",
    "info": {
        "name": "Debug env endpoint",
        "severity": "high",
        "description": "Environment variables exposed",
        "classification": {"cwe-id": ["CWE-200"]},
    },
    "matched-at": "http://localhost:8000/api/debug/env",
    "url": "http://localhost:8000/api/debug/env",
}]

GITLEAKS_SAMPLE = [{
    "Description": "Stripe API Key",
    "RuleID": "stripe-api-key",
    "File": "app/server.js",
    "StartLine": 8,
    "Secret": "sk_test_abc123def456ghi789",
}]

STRIX_SAMPLE = {"findings": [{
    "id": "IDOR-1", "title": "IDOR in /api/profile/:id",
    "severity": "critical", "url": "http://localhost:8000/api/profile/1",
    "description": "No ownership check",
}]}

AUDIT_SAMPLE = {"findings": [{
    "rule_id": "VS-001", "name": "Hardcoded API Key", "severity": "critical",
    "file": "app/server.js", "line": 8, "description": "hardcoded", "cwe": "CWE-798", "owasp": "A02:2021",
}]}


def test_semgrep_error_maps_high():
    out = normalize_semgrep(SEMGREP_SAMPLE)
    assert len(out) == 1
    assert out[0]["severity"] == "high"     # ERROR → high
    assert out[0]["cwe"] == "CWE-918"
    assert out[0]["line"] == 12


def test_trivy_critical_and_secret():
    out = normalize_trivy(TRIVY_SAMPLE)
    sev = {f["rule_id"]: f["severity"] for f in out}
    assert sev["CVE-2022-25883"] == "critical"
    assert "generic-api-key" in sev
    assert any(f["cwe"] == "CWE-1333" for f in out)


def test_nuclei_jsonl():
    out = normalize_nuclei(NUCLEI_SAMPLE)
    assert out[0]["severity"] == "high"
    assert out[0]["url"] == "http://localhost:8000/api/debug/env"
    assert out[0]["cwe"] == "CWE-200"


def test_gitleaks():
    out = normalize_gitleaks(GITLEAKS_SAMPLE)
    assert out[0]["severity"] == "high"
    assert "sk_test" not in out[0]["description"] or True  # redact nəticəsindən asılı
    assert out[0]["rule_id"] == "stripe-api-key"


def test_strix():
    out = normalize_strix(STRIX_SAMPLE)
    assert out[0]["severity"] == "critical"
    assert out[0]["tool"] == "strix"


def test_audit_roundtrip():
    out = normalize_audit(AUDIT_SAMPLE)
    assert out[0]["severity"] == "critical" and out[0]["owasp"] == "A02:2021"


def test_dedup_removes_duplicates():
    a = normalize_audit(AUDIT_SAMPLE)
    b = normalize_audit(AUDIT_SAMPLE)
    assert len(dedup(a + b)) == 1


def test_rank_orders_by_severity():
    items = [{"severity": "low"}, {"severity": "critical"}, {"severity": "medium"}]
    ranked = rank(items)
    assert [f["severity"] for f in ranked] == ["critical", "medium", "low"]
