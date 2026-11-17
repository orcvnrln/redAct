"""
Deterministik Gate — JSON-dan oxuyur, LLM müdaxilə etmir.
desktop_app.gate ilə eyni qərar məntiqi, orchestrator şeması ilə.
"""

import json
import os
from typing import Dict, Any, List, Tuple


class DeterministicGate:
    def __init__(self, fail_on: List[str] = None):
        self.fail_on = fail_on or ["critical", "high"]

    def evaluate(self, findings: List[Dict[str, Any]]) -> Tuple[bool, Dict[str, int], List[Dict[str, Any]]]:
        counts: Dict[str, int] = {}
        blocking: List[Dict[str, Any]] = []
        for f in findings:
            sev = str(f.get("severity", "unknown")).lower()
            counts[sev] = counts.get(sev, 0) + 1
            if sev in self.fail_on:
                blocking.append(f)
        return (len(blocking) == 0), counts, blocking

    def decision(self, findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        passed, counts, blocking = self.evaluate(findings)
        return {
            "passed": passed,
            "fail_on": self.fail_on,
            "severity_counts": counts,
            "blocking_count": len(blocking),
            "decision": "BLOCK" if not passed else "ALLOW",
            "reason": (f"{len(blocking)} {self.fail_on} severity tapıntı — deploy bloklandı"
                       if not passed else f"{self.fail_on} severity tapıntı yoxdur — keçir"),
            "blocking_findings": blocking[:50],
            "deterministic": True,
            "llm_involved": False,
        }

    @staticmethod
    def write(unified: Dict[str, Any], path: str) -> None:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(unified, f, indent=2, ensure_ascii=False)
