"""
Audit Motor — 13 Deterministik Qayda
Regex əsaslı, LLM-siz təhlükəsizlik yoxlamaları
"""

import re
from typing import List, Dict, Any
from pathlib import Path


class AuditRule:
    def __init__(self, rule_id: str, name: str, severity: str, pattern: str, 
                 description: str, cwe: str = "", owasp: str = ""):
        self.rule_id = rule_id
        self.name = name
        self.severity = severity.lower()
        self.pattern = re.compile(pattern, re.IGNORECASE | re.MULTILINE)
        self.description = description
        self.cwe = cwe
        self.owasp = owasp

    def check(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Faylda qaydanı yoxlayır və tapıntılar qaytarır"""
        findings = []
        for match in self.pattern.finditer(content):
            line_num = content[:match.start()].count('\n') + 1
            findings.append({
                "rule_id": self.rule_id,
                "name": self.name,
                "severity": self.severity,
                "file": file_path,
                "line": line_num,
                "match": match.group(0)[:100],  # İlk 100 simvol
                "description": self.description,
                "cwe": self.cwe,
                "owasp": self.owasp,
            })
        return findings


# 13 Əsas Qayda Dəsti
RULES = [
    # 1. Hardcoded Secrets
    AuditRule(
        rule_id="VS-001",
        name="Hardcoded API Key",
        severity="critical",
        pattern=r'(api[_-]?key|apikey|api[_-]?secret)\s*[=:]\s*[\'"][a-zA-Z0-9_\-]{20,}[\'"]',
        description="API key hardcoded olunub - secret management istifadə edin",
        cwe="CWE-798",
        owasp="A02:2021"
    ),
    
    # 2. SQL Injection Pattern
    AuditRule(
        rule_id="VS-002",
        name="SQL Injection Risk",
        severity="critical",
        pattern=r'(execute|exec|query)\s*\(\s*[\'"`]?\s*SELECT.*?\+.*?\)',
        description="SQL sorğusunda string konkatenasiyası - parametrləşdirmə istifadə edin",
        cwe="CWE-89",
        owasp="A03:2021"
    ),
    
    # 3. Path Traversal
    AuditRule(
        rule_id="VS-003",
        name="Path Traversal",
        severity="high",
        pattern=r'(open|readFile|readFileSync)\s*\([^)]*(\.\./|\.\.\\)',
        description="Path traversal riski - fayl yolunu valide edin",
        cwe="CWE-22",
        owasp="A01:2021"
    ),
    
    # 4. XSS - Dangerous HTML
    AuditRule(
        rule_id="VS-004",
        name="XSS via innerHTML",
        severity="high",
        pattern=r'\.innerHTML\s*=\s*(?!["\']\w)',
        description="innerHTML istifadə olunur - sanitize edin və ya textContent istifadə edin",
        cwe="CWE-79",
        owasp="A03:2021"
    ),
    
    # 5. Weak Crypto
    AuditRule(
        rule_id="VS-005",
        name="Weak Cryptography",
        severity="high",
        pattern=r'(md5|sha1|des)[\s\(]',
        description="Zəif kriptoqrafiya alqoritmi - SHA256+ istifadə edin",
        cwe="CWE-327",
        owasp="A02:2021"
    ),
    
    # 6. Debug Endpoints
    AuditRule(
        rule_id="VS-006",
        name="Debug/Admin Endpoint",
        severity="high",
        pattern=r'/(debug|admin|test|internal)/',
        description="Debug/admin endpoint production-da açıq qala bilər",
        cwe="CWE-489",
        owasp="A05:2021"
    ),
    
    # 7. Missing Auth Check
    AuditRule(
        rule_id="VS-007",
        name="Missing Authorization",
        severity="critical",
        pattern=r'app\.(get|post|put|delete)\([^)]*\)\s*,\s*(?!.*auth)',
        description="Route-da auth middleware yoxdur",
        cwe="CWE-285",
        owasp="A01:2021"
    ),
    
    # 8. IDOR Pattern
    AuditRule(
        rule_id="VS-008",
        name="IDOR Risk",
        severity="high",
        pattern=r'req\.params\.(id|userId|user_id).*find.*\bOne\b',
        description="IDOR riski - ownership yoxlaması əlavə edin",
        cwe="CWE-639",
        owasp="A01:2021"
    ),
    
    # 9. Eval Usage
    AuditRule(
        rule_id="VS-009",
        name="Code Injection via eval()",
        severity="critical",
        pattern=r'\beval\s*\(',
        description="eval() istifadəsi - RCE riski",
        cwe="CWE-95",
        owasp="A03:2021"
    ),
    
    # 10. Insecure Randomness
    AuditRule(
        rule_id="VS-010",
        name="Insecure Random",
        severity="medium",
        pattern=r'Math\.random\(\)',
        description="Math.random() kriptqrafik təhlükəsizlik üçün uyğun deyil",
        cwe="CWE-330",
        owasp="A02:2021"
    ),
    
    # 11. CORS Misconfiguration
    AuditRule(
        rule_id="VS-011",
        name="CORS Wildcard",
        severity="high",
        pattern=r'Access-Control-Allow-Origin[\'"]?\s*:\s*[\'"]?\*',
        description="CORS wildcard (*) istifadə olunur",
        cwe="CWE-942",
        owasp="A05:2021"
    ),
    
    # 12. Password in Code
    AuditRule(
        rule_id="VS-012",
        name="Hardcoded Password",
        severity="critical",
        pattern=r'(password|passwd|pwd)\s*[=:]\s*[\'"][^\'"]{3,}[\'"]',
        description="Şifrə hardcoded olunub",
        cwe="CWE-259",
        owasp="A07:2021"
    ),
    
    # 13. Missing HTTPS
    AuditRule(
        rule_id="VS-013",
        name="HTTP URL in Production",
        severity="medium",
        pattern=r'http://(?!localhost|127\.0\.0\.1)',
        description="HTTP URL production kodunda - HTTPS istifadə edin",
        cwe="CWE-319",
        owasp="A02:2021"
    ),
]


class AuditEngine:
    def __init__(self, rules: List[AuditRule] = None):
        self.rules = rules or RULES

    def scan_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Tək faylı skan edir"""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            return []

        all_findings = []
        for rule in self.rules:
            findings = rule.check(content, str(file_path))
            all_findings.extend(findings)

        return all_findings

    def scan_project(self, project_path: Path, extensions: List[str] = None) -> List[Dict[str, Any]]:
        """Bütün proyekti skan edir"""
        if extensions is None:
            extensions = ['.js', '.ts', '.py', '.java', '.go', '.php', '.rb']

        all_findings = []
        for ext in extensions:
            for file_path in project_path.rglob(f'*{ext}'):
                # node_modules, venv və s. atlayırıq
                if any(p in file_path.parts for p in ['node_modules', 'venv', '.git', 'dist', 'build']):
                    continue
                findings = self.scan_file(file_path)
                all_findings.extend(findings)

        return all_findings

    def get_summary(self, findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Tapıntıların xülasəsi"""
        severity_counts = {}
        for f in findings:
            sev = f['severity']
            severity_counts[sev] = severity_counts.get(sev, 0) + 1

        return {
            "total": len(findings),
            "critical": severity_counts.get('critical', 0),
            "high": severity_counts.get('high', 0),
            "medium": severity_counts.get('medium', 0),
            "low": severity_counts.get('low', 0),
            "by_rule": self._group_by_rule(findings)
        }

    def _group_by_rule(self, findings: List[Dict[str, Any]]) -> Dict[str, int]:
        """Qaydalara görə qruplaşdırma"""
        grouped = {}
        for f in findings:
            rule_id = f['rule_id']
            grouped[rule_id] = grouped.get(rule_id, 0) + 1
        return grouped
