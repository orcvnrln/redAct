"""
Report Generator — unified_findings.json + report.md ( insan üçün ).
Yalnız real məlumat: tool statusları, tapıntı cədvəli, gate qərarı.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

from .tools import ToolStatus


def write_json(unified: Dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(unified, indent=2, ensure_ascii=False), encoding="utf-8")


def _status_badge(status: str) -> str:
    return {
        ToolStatus.OK: "✅ OK",
        ToolStatus.FAILED: "❌ FAILED",
        ToolStatus.SKIPPED: "⏭️ SKIPPED",
        ToolStatus.TIMEOUT: "⏱️ TIMEOUT",
        ToolStatus.NOT_FOUND: "🚫 NOT_FOUND",
    }.get(status, status)


def write_markdown(unified: Dict[str, Any], out_dir: Path, fail_on: List[str]) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / "report.md"
    findings: List[dict] = unified.get("findings", [])
    tools: List[dict] = unified.get("tools", [])
    gate: Dict[str, Any] = unified.get("gate", {})

    counts = gate.get("severity_counts", {})
    lines = [
        "# 🛡️ VibeShield — Tam Avtonom DevSecOps Hesabatı",
        f"",
        f"**Tarix:** {datetime.now().isoformat()}  ",
        f"**Proyekt:** `{unified.get('project', '')}`  ",
        f"**Live hədəf:** `{unified.get('target') or 'yoxdur (yalnız statik)'}`  ",
        f"**Profil:** `{unified.get('profile', '')}`",
        "",
        "## 🔀 Gate Qərarı (deterministik, LLM-siz)",
        "",
        f"## {'❌ BLOKLANDI' if gate.get('decision') == 'BLOCK' else '✅ KEÇDİ'} — {gate.get('reason', '')}",
        "",
        "| Severity | Say |",
        "|---|---|",
        f"| critical | {counts.get('critical', 0)} |",
        f"| high | {counts.get('high', 0)} |",
        f"| medium | {counts.get('medium', 0)} |",
        f"| low | {counts.get('low', 0)} |",
        f"| info | {counts.get('info', 0)} |",
        "",
        "## 🧰 Tool Statusları",
        "",
        "| Tool | Status | Tapıntı | Müddət | Qeyd |",
        "|---|---|---|---|---|",
    ]
    for t in tools:
        lines.append(
            f"| {t['name']} | {_status_badge(t['status'])} | {t.get('findings_count', 0)} | "
            f"{t.get('duration_s', 0)}s | {(t.get('reason') or '—')[:80]} |"
        )

    lines += ["", "## 🚨 Tapıntılar (critical→info sıralı)", ""]
    if findings:
        for i, f in enumerate(findings, 1):
            loc = f.get("url") or (f"{f.get('file', '')}:{f.get('line', '')}" if f.get("file") else "—")
            lines += [
                f"### {i}. [{f['severity'].upper()}] {f['title']}  ({f['tool']})",
                f"- **Yer:** `{loc}`",
                f"- **CWE/OWASP:** {f.get('cwe') or '—'} / {f.get('owasp') or '—'}",
                f"- **Təsvir:** {(f.get('description') or '—')[:300]}",
                "",
            ]
    else:
        lines.append("_Tapıntı yoxdur._")

    lines += [
        "",
        "## 📎 Fayllar",
        "",
        f"- `unified_findings.json` — hamıdan vahid formatda",
    ]
    for t in tools:
        if t.get("raw_file"):
            lines.append(f"- `{t['raw_file']}` — {t['name']} raw nəticə")

    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path
