"""
DevSecOps Desktop Tool — Deterministic Gate Module
Addım 6: jq + unified_findings.json. LLM-qədar olmayan qərar.
"""

import json
import os
from typing import Dict, Any, List, Tuple


class DeterministicGate:
    def __init__(self, severity_threshold: List[str] = None):
        self.severity_threshold = severity_threshold or ["critical", "high"]

    def load_json(self, path: str) -> Any:
        if not os.path.exists(path):
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None

    def unify_findings(self, file_paths: List[str], output_path: str = "unified_findings.json", audit_findings_path: str = None) -> Dict[str, Any]:
        """Birləşdiriləcək bütün JSON fayllarını oxuyub vahid findings.json yaradır."""
        all_findings = []

        # Əvvəlcə audit motorundan nəticələri əlavə et
        if audit_findings_path and os.path.exists(audit_findings_path):
            audit_data = self.load_json(audit_findings_path)
            if audit_data and "findings" in audit_data:
                for f in audit_data["findings"]:
                    all_findings.append({
                        "tool": "audit_engine",
                        "severity": f.get("severity", "UNKNOWN").lower(),
                        "title": f.get("name", f.get("rule_id", "audit finding")),
                        "description": f.get("description", ""),
                        "file": f.get("file", ""),
                        "line": f.get("line", 0),
                        "rule_id": f.get("rule_id", ""),
                        "cwe": f.get("cwe", ""),
                        "owasp": f.get("owasp", ""),
                    })

        for path in file_paths:
            data = self.load_json(path)
            if data is None:
                continue

            # Semgrep format: {"results": [...]}
            if isinstance(data, dict) and "results" in data:
                for r in data["results"]:
                    all_findings.append({
                        "tool": "semgrep",
                        "severity": r.get("extra", {}).get("severity", "UNKNOWN").lower(),
                        "title": r.get("check_id", "semgrep finding"),
                        "description": r.get("extra", {}).get("message", ""),
                        "file": r.get("path", ""),
                        "line": r.get("start", {}).get("line", 0),
                    })

            # Trivy format: {"Results": [{"Vulnerabilities": [...]}]}
            elif isinstance(data, dict) and "Results" in data:
                for res in data["Results"]:
                    for v in res.get("Vulnerabilities", []):
                        all_findings.append({
                            "tool": "trivy",
                            "severity": v.get("Severity", "UNKNOWN").lower(),
                            "title": v.get("Title", v.get("VulnerabilityID", "trivy finding")),
                            "description": v.get("Description", ""),
                            "file": v.get("PkgName", ""),
                            "line": 0,
                        })

            # Strix / generic format: {"findings": [...]}
            elif isinstance(data, dict) and "findings" in data:
                for r in data["findings"]:
                    all_findings.append({
                        "tool": r.get("tool", "unknown"),
                        "severity": r.get("severity", "UNKNOWN").lower(),
                        "title": r.get("title", r.get("id", "finding")),
                        "description": r.get("description", r.get("message", "")),
                        "file": r.get("file", ""),
                        "line": r.get("line", 0),
                    })

            # Nuclei format: list of objects or single object
            elif isinstance(data, list):
                for r in data:
                    all_findings.append({
                        "tool": "nuclei",
                        "severity": r.get("info", {}).get("severity", "UNKNOWN").lower() if isinstance(r, dict) else "UNKNOWN",
                        "title": r.get("info", {}).get("name", "nuclei finding") if isinstance(r, dict) else "nuclei finding",
                        "description": r.get("info", {}).get("description", "") if isinstance(r, dict) else str(r),
                        "file": r.get("matched-at", "") if isinstance(r, dict) else "",
                        "line": 0,
                    })

        unified = {"findings": all_findings, "count": len(all_findings)}

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(unified, f, indent=2, ensure_ascii=False)

        return unified

    def evaluate(self, unified_path: str = "unified_findings.json") -> Tuple[bool, int, Dict[str, int]]:
        """
        Deterministik qapı.
        Ger qaydırır: (keçdi_mi, kritik_say, severity_sayları)
        Qərar yalnız JSON-dan oxunur — LLM müdaxilə etmir.
        """
        data = self.load_json(unified_path)
        if data is None or "findings" not in data:
            return True, 0, {}

        findings: List[Dict[str, Any]] = data["findings"]
        severity_counts: Dict[str, int] = {}

        critical_count = 0
        for f in findings:
            sev = str(f.get("severity", "UNKNOWN")).lower()
            severity_counts[sev] = severity_counts.get(sev, 0) + 1
            if sev in self.severity_threshold:
                critical_count += 1

        passed = critical_count == 0
        return passed, critical_count, severity_counts

    def gate_report(self, unified_path: str = "unified_findings.json") -> Dict[str, Any]:
        passed, critical_count, severity_counts = self.evaluate(unified_path)
        return {
            "passed": passed,
            "critical_count": critical_count,
            "severity_counts": severity_counts,
            "decision": "PUBLISH BLOKLANDI" if not passed else "PUBLISH-Ə İCAZƏ VERİLİR",
            "reason": f"{critical_count} kritik/yüksək zəiflik tapıldı" if critical_count > 0 else "Zəiflik tapılmadı",
            "deterministic": True,
            "llm_involved": False,
        }