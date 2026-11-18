"""
Tool Runner-lər — hər bir security tool üçün real CLI wrapper.
Hər runner qaytarır: ExecResult (real icra) + findings (normalizasiya olunmuş).
Status dəyişməyən kod yoxdur: tool yoxdursa SKIPPED, xəta varsa FAILED.
"""

import json
import shutil
from pathlib import Path
from typing import List, Optional

from ..runner import ToolRunner, ExecResult
from .. import unified
from ..unified import normalize_audit, normalize_semgrep, normalize_gitleaks, \
    normalize_trivy, normalize_nuclei, normalize_strix, dedup, rank

import re as _re

_ANSI_RE = _re.compile(r"\x1b\[[0-9;]*[A-Za-z]")


def _strip_ansi(s: str) -> str:
    return _ANSI_RE.sub("", s)


class ToolStatus:
    OK = "OK"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    TIMEOUT = "TIMEOUT"
    NOT_FOUND = "NOT_FOUND"
    CANCELLED = "CANCELLED"


class BaseTool:
    """Bir tool-un icra + nəticə toplama kontraktı."""

    name: str = "base"
    # seed rule id/names for report table
    description: str = ""

    def __init__(self, binary: Optional[str] = None, timeout: int = 600, retries: int = 0,
                 env_extra: Optional[dict] = None, cwd: Optional[str] = None):
        self.binary = binary          # resolve() nəticəsi; None = yok
        self.runner = ToolRunner(timeout=timeout, retries=retries, env_extra=env_extra, cwd=cwd)
        self.status: str = ToolStatus.NOT_FOUND
        self.reason: str = ""
        self.exec_result: Optional[ExecResult] = None
        self.findings: List[dict] = []
        self.line_callback = None     # Pipeline təyin edir: canlı sətir axını

    @property
    def available(self) -> bool:
        # audit_engine kimi daxili tool-lar üçün binary None ola bilməz, amma "internal" yazılır
        return self.binary is not None

    def _emit_line(self, line: str) -> None:
        if self.line_callback:
            try:
                self.line_callback(_strip_ansi(line))
            except Exception:
                pass

    def cancel(self) -> bool:
        """İşlək subprocess-i öldürür."""
        return self.runner.cancel()

    def run(self, project: Path, out_dir: Path, target: Optional[str]) -> None:
        raise NotImplementedError

    def _finish(self, exec_result: ExecResult, ok_codes: tuple = (0,), parse=None,
                findings_file: Optional[Path] = None):
        self.exec_result = exec_result
        if exec_result.not_found:
            self.status = ToolStatus.NOT_FOUND
            self.reason = exec_result.error or "binary yoxdur"
            return
        if exec_result.timed_out:
            self.status = ToolStatus.TIMEOUT
            self.reason = exec_result.error or ""
            return
        if exec_result.exit_code is not None and exec_result.exit_code < 0:
            self.status = ToolStatus.FAILED
            self.reason = f"proses dayandırıldı (signal {-exec_result.exit_code})"
            return
        if exec_result.exit_code in ok_codes:
            self.status = ToolStatus.OK
            self.reason = ""
        else:
            self.status = ToolStatus.FAILED
            self.reason = f"exit {exec_result.exit_code}: {(exec_result.output_all() or '')[-400:]}"

        if findings_file and findings_file.is_file():
            try:
                raw = json.loads(findings_file.read_text(encoding="utf-8", errors="ignore"))
            except json.JSONDecodeError:
                # JSONL (nuclei) fallback
                raw = []
                for line in findings_file.read_text(encoding="utf-8", errors="ignore").splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        raw.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
            except Exception as e:  # noqa
                self.findings = []
                return
            if parse:
                self.findings = parse(raw)


class AuditEngineTool(BaseTool):
    name = "audit_engine"
    description = "Regex əsaslı deterministik SAST (repo daxili, 13 qayda)"

    def run(self, project: Path, out_dir: Path, target: Optional[str]) -> None:
        out_dir.mkdir(parents=True, exist_ok=True)
        findings_file = out_dir / "audit_findings.json"

        self._emit_line("[audit] 13 qayda yükləndi — regex əsaslı SAST")
        # Modul kimi çağırırıq — subprocess-overhead yoxdur, nəticə eynidir
        from audit.rules import AuditEngine
        try:
            engine = AuditEngine()
            self._emit_line(f"[audit] skan başlayır: {project}")
            findings = engine.scan_project(project)
            summary = engine.get_summary(findings)
            self._emit_line(f"[audit] {summary['total']} tapıntı (critical={summary['critical']}, high={summary['high']})")
        except Exception as e:
            self.status = ToolStatus.FAILED
            self.reason = f"audit engine xətası: {e}"
            return

        payload = {"findings": findings, "summary": summary, "deterministic": True, "llm_involved": False}
        findings_file.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

        self.exec_result = ExecResult(command=[f"python -m audit.run_audit --project {project}"],
                                      exit_code=0, stdout=json.dumps(summary, ensure_ascii=False))
        self.status = ToolStatus.OK
        self.findings = normalize_audit(payload)


class SemgrepTool(BaseTool):
    name = "semgrep"
    description = "Semgrep SAST (registry qaydaları)"

    def run(self, project: Path, out_dir: Path, target: Optional[str]) -> None:
        if not self.available:
            self.reason = "semgrep binary yoxdur"
            return
        out_dir.mkdir(parents=True, exist_ok=True)
        findings_file = out_dir / "semgrep.json"
        cmd = [
            self.binary,
            "scan", "--config", "auto", "--json",
            "--output", str(findings_file),
            "--quiet",
            "--exclude", "node_modules",
            "--exclude", "scan_out",
            "--exclude", ".venv",
            str(project),
        ]
        exec_result = self.runner.exec(cmd, on_line=self._emit_line)
        # semgrep: 0=təmiz, 1=tapıntı var
        self._finish(exec_result, ok_codes=(0, 1), parse=normalize_semgrep, findings_file=findings_file)
        if self.status == ToolStatus.OK and not findings_file.is_file():
            self.findings = []


class GitleaksTool(BaseTool):
    name = "gitleaks"
    description = "Secrets scanner (git tarixçəsi + working tree)"

    def run(self, project: Path, out_dir: Path, target: Optional[str]) -> None:
        if not self.available:
            self.reason = "gitleaks binary yoxdur"
            return
        out_dir.mkdir(parents=True, exist_ok=True)
        findings_file = out_dir / "gitleaks.json"
        cmd = [
            self.binary, "detect",
            "--source", str(project),
            "--report-format", "json",
            "--report-path", str(findings_file),
            "--exit-code", "0",       # tapıntı olsa da çökməsini istəmirik; qərar gate-dədir
            "--redact",               # secret dəyəri hesabatda maskalanır
        ]
        if not (project / ".git").exists():
            cmd.append("--no-git")    # git tarixçəsi olmayan kataloq
        exec_result = self.runner.exec(cmd, on_line=self._emit_line)
        self._finish(exec_result, ok_codes=(0,), parse=normalize_gitleaks, findings_file=findings_file)


class TrivyTool(BaseTool):
    name = "trivy"
    description = "SCA + IaC + secret (npm/pip dependencies)"

    def run(self, project: Path, out_dir: Path, target: Optional[str]) -> None:
        if not self.available:
            self.reason = "trivy binary yoxdur"
            return
        out_dir.mkdir(parents=True, exist_ok=True)
        findings_file = out_dir / "trivy.json"
        cmd = [
            self.binary, "fs",
            "--scanners", "vuln,secret,misconfig",
            "--severity", "LOW,MEDIUM,HIGH,CRITICAL",
            "--format", "json",
            "--output", str(findings_file),
            "--skip-dirs", "node_modules,scan_out,.venv",
            str(project),
        ]
        exec_result = self.runner.exec(cmd, on_line=self._emit_line)
        self._finish(exec_result, ok_codes=(0,), parse=normalize_trivy, findings_file=findings_file)


class NucleiTool(BaseTool):
    name = "nuclei"
    description = "DAST template scanner (live hədəf)"

    def run(self, project: Path, out_dir: Path, target: Optional[str]) -> None:
        if not self.available:
            self.reason = "nuclei binary yoxdur"
            return
        if not target:
            self.status = ToolStatus.SKIPPED
            self.reason = "live hədəf verilməyib (--target)"
            return
        out_dir.mkdir(parents=True, exist_ok=True)
        findings_file = out_dir / "nuclei.jsonl"
        cmd = [
            self.binary,
            "-target", target,
            "-jle", str(findings_file),
            "-timeout", "10",
            "-retries", "1",
            "-silent",
        ]
        exec_result = self.runner.exec(cmd, on_line=self._emit_line)
        # nuclei: 0=tapıntı yox, 1=tapıntı var
        self._finish(exec_result, ok_codes=(0, 1), parse=normalize_nuclei, findings_file=findings_file)


class StrixTool(BaseTool):
    name = "strix"
    description = "AI pentest agent (LLM açar + Docker tələb edir)"

    @staticmethod
    def _newest_vuln(runs_dir: Path, exclude: Optional[set] = None) -> Optional[Path]:
        if not runs_dir.is_dir():
            return None
        cands = [p for p in runs_dir.glob("*/vulnerabilities.json")
                 if p.is_file() and p.parent.name not in (exclude or set())]
        return max(cands, key=lambda p: p.stat().st_mtime) if cands else None

    def run(self, project: Path, out_dir: Path, target: Optional[str]) -> None:
        if not self.available:
            self.reason = "strix binary yoxdur"
            return
        if not shutil.which("docker"):
            self.status = ToolStatus.SKIPPED
            self.reason = "Docker yoxdur (strix sandbox tələb edir)"
            return
        key = self.runner.env_extra.get("LLM_API_KEY", "")
        if not key:
            self.status = ToolStatus.SKIPPED
            self.reason = "LLM_API_KEY yoxdur (strix AI agent üçün açar tələb edir)"
            return
        if not target:
            self.status = ToolStatus.SKIPPED
            self.reason = "live hədəf verilməyib"
            return

        out_dir.mkdir(parents=True, exist_ok=True)
        cwd = Path(getattr(self.runner, "cwd", None) or Path.cwd())
        runs_dir = cwd / "strix_runs"
        # Köhnə run-un nəticəsini bu run-a aid etməmək üçün əvvəlcədən snapshot.
        before = {p.parent.name for p in runs_dir.glob("*/vulnerabilities.json")}
        # Strix nəticəni --output ilə yox, <cwd>/strix_runs/<run>/vulnerabilities.json-a yazır.
        cmd = [
            self.binary, "-n",
            "--target", target,
            "--scan-mode", "quick",
            "--max-turns", "40",
        ]
        exec_result = self.runner.exec(cmd, on_line=self._emit_line)
        vuln_file = self._newest_vuln(runs_dir, exclude=before)
        if vuln_file:
            # exit 2 = tapıntı var (--fail-on default), 0 = təmiz
            self._finish(exec_result, ok_codes=(0, 2), parse=normalize_strix,
                         findings_file=vuln_file)
            if self.status == ToolStatus.OK:
                self.reason = f"strix run: {vuln_file.parent.name}"
        elif exec_result.exit_code == 0:
            self._finish(exec_result, ok_codes=(0,))
            self.reason = "strix bitdi — tapıntı faylı yoxdur (təmiz run)"
        else:
            self.exec_result = exec_result
            self.status = ToolStatus.FAILED
            self.reason = f"exit {exec_result.exit_code}: {(exec_result.output_all() or '')[-300:]}"


TOOL_REGISTRY = {
    "audit_engine": AuditEngineTool,
    "semgrep": SemgrepTool,
    "gitleaks": GitleaksTool,
    "trivy": TrivyTool,
    "nuclei": NucleiTool,
    "strix": StrixTool,
}


def collect_findings(tools: List[BaseTool]) -> List[dict]:
    all_f = []
    for t in tools:
        all_f.extend(t.findings)
    return rank(dedup(all_f))
