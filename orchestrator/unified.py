"""
Unified Schema — hər tool öz JSON formatında danışır; biz hamısını
bir dilə gətiririk. Yalnız real, tool-dan gələn məlumat normalizasiya olunur.

Vahid tapıntı:
{
  "tool": str, "severity": "critical|high|medium|low|info",
  "title": str, "description": str,
  "file": str, "line": int,
  "url": str,       # DAST tapıntı üçün
  "rule_id": str, "cwe": str, "owasp": str
}
"""

from typing import Any, Dict, List

SEVERITY_ORDER = ["critical", "high", "medium", "low", "info", "unknown"]


def _norm_sev(raw: Any) -> str:
    s = str(raw).strip().lower()
    s = s.replace("warning", "medium").replace("error", "high")
    if s not in SEVERITY_ORDER:
        s = "unknown"
    return s


def normalize_audit(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    out = []
    for f in data.get("findings", []):
        out.append({
            "tool": "audit_engine",
            "severity": _norm_sev(f.get("severity")),
            "title": f.get("name") or f.get("rule_id", "audit finding"),
            "description": f.get("description", ""),
            "file": f.get("file", ""),
            "line": int(f.get("line", 0) or 0),
            "url": "",
            "rule_id": f.get("rule_id", ""),
            "cwe": f.get("cwe", ""),
            "owasp": f.get("owasp", ""),
        })
    return out


def normalize_semgrep(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    out = []
    for r in data.get("results", []):
        extra = r.get("extra", {}) or {}
        meta = extra.get("metadata", {}) or {}
        out.append({
            "tool": "semgrep",
            "severity": _norm_sev(extra.get("severity", r.get("severity", "UNKNOWN"))),
            "title": r.get("check_id", "semgrep finding"),
            "description": extra.get("message", ""),
            "file": r.get("path", ""),
            "line": int((r.get("start", {}) or {}).get("line", 0) or 0),
            "url": "",
            "rule_id": r.get("check_id", ""),
            "cwe": str(meta.get("cwe", "")),
            "owasp": str(meta.get("owasp", "")),
        })
    return out


def normalize_gitleaks(data: Any) -> List[Dict[str, Any]]:
    # gitleaks: root səviyyədə sıralı obyektlər (stdout) və ya report sırası
    if isinstance(data, dict):
        data = data.get("findings", [])
    out = []
    for f in data or []:
        if not isinstance(f, dict):
            continue
        out.append({
            "tool": "gitleaks",
            "severity": "high",          # hər real leak secret təsiridir
            "title": f.get("Description") or f.get("RuleID", "gitleaks secret"),
            "description": f"Secret: {f.get('Secret', '')[:60]}…",
            "file": f.get("File", ""),
            "line": int(f.get("StartLine", 0) or 0),
            "url": "",
            "rule_id": f.get("RuleID", ""),
            "cwe": "CWE-798",
            "owasp": "A02:2021",
        })
    return out


def normalize_trivy(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    out = []
    for res in data.get("Results", []) or []:
        kind = res.get("Class", "")
        for v in res.get("Vulnerabilities", []) or []:
            out.append({
                "tool": "trivy",
                "severity": _norm_sev(v.get("Severity")),
                "title": f"{v.get('VulnerabilityID', 'CVE')}: {v.get('PkgName', '')}",
                "description": (v.get("Title") or v.get("Description") or "")[:300],
                "file": res.get("Target", ""),
                "line": 0,
                "url": v.get("PrimaryURL", ""),
                "rule_id": v.get("VulnerabilityID", ""),
                "cwe": _first_cwe(v.get("CweIDs", [])),
                "owasp": "",
            })
        # secret scan nəticələri (trivy secrets)
        for s in res.get("Secrets", []) or []:
            out.append({
                "tool": "trivy",
                "severity": "high",
                "title": s.get("Title", "trivy secret"),
                "description": f"Secret tapıldı ({s.get('Match', '')[:40]})",
                "file": res.get("Target", ""),
                "line": int(s.get("StartLine", 0) or 0),
                "url": "",
                "rule_id": s.get("RuleID", ""),
                "cwe": "CWE-798",
                "owasp": "",
            })
        # misconfiguration tapıntıları (dockerfile/iac)
        for m in res.get("Misconfigurations", []) or []:
            out.append({
                "tool": "trivy",
                "severity": _norm_sev(m.get("Severity")),
                "title": f"{m.get('ID', '')}: {m.get('Title', 'misconfig')}",
                "description": m.get("Description", ""),
                "file": res.get("Target", ""),
                "line": 0,
                "url": "",
                "rule_id": m.get("ID", ""),
                "cwe": "",
                "owasp": "",
            })
    return out


def normalize_nuclei(data: Any) -> List[Dict[str, Any]]:
    # nuclei -json: hər sətir ayrı JSON obyekt (JSONL) və ya sıra
    items = data if isinstance(data, list) else []
    if isinstance(data, dict) and "findings" in data:
        items = data["findings"]
    out = []
    for r in items:
        if not isinstance(r, dict):
            continue
        info = r.get("info", {}) or {}
        sev = info.get("severity", "UNKNOWN")
        out.append({
            "tool": "nuclei",
            "severity": _norm_sev(sev),
            "title": info.get("name", r.get("template-id", "nuclei finding")),
            "description": (info.get("description") or "")[:300],
            "file": "",                                  # DAST — fayl yoxdur
            "line": 0,
            "url": r.get("matched-at") or r.get("url", ""),
            "rule_id": r.get("template-id", ""),
            "cwe": _first_cwe(_cwe_list(info)),
            "owasp": "",
        })
    return out


def normalize_strix(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    out = []
    for f in data.get("findings", []) or []:
        if not isinstance(f, dict):
            continue
        out.append({
            "tool": "strix",
            "severity": _norm_sev(f.get("severity")),
            "title": f.get("title", f.get("id", "strix finding")),
            "description": f.get("description", f.get("message", "")),
            "file": f.get("file", ""),
            "line": int(f.get("line", 0) or 0),
            "url": f.get("url", ""),
            "rule_id": f.get("id", ""),
            "cwe": f.get("cwe", ""),
            "owasp": "",
        })
    return out


def _first_cwe(cwes: Any) -> str:
    if not cwes:
        return ""
    if isinstance(cwes, str):
        return cwes
    try:
        return str(list(cwes)[0])
    except Exception:
        return ""


def _cwe_list(info: dict) -> list:
    cl = info.get("classification") or {}
    if isinstance(cl, dict):
        return cl.get("cwe-id", []) or []
    return []


def dedup(findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Eyni (tool, rule, fayl, sətir, url) tapıntıları birləşdirir."""
    seen: Dict[tuple, Dict[str, Any]] = {}
    out = []
    for f in findings:
        key = (f["tool"], f.get("rule_id", ""), f.get("file", ""), f.get("line", 0), f.get("url", ""))
        if key in seen:
            continue
        seen[key] = f
        out.append(f)
    return out


def rank(findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Ciddilik sırası ilə: critical → info."""
    order = {s: i for i, s in enumerate(SEVERITY_ORDER)}
    return sorted(findings, key=lambda f: order.get(f["severity"], 99))
