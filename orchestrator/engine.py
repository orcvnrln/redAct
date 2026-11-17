"""
Pipeline Engine — stage qrafikası, paralel statik skanlar, ardıcıllıq gate.
Tam avtonom: hədəf gözləmə, live server yoxlama, status reallığı.
"""

import shutil
import socket
import time
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, Any, List, Optional, Type

from . import unified as U
from .runner import ExecResult
from .gate import DeterministicGate
from .report import write_json, write_markdown
from .resolver import resolve, REPO_ROOT
from .tools import TOOL_REGISTRY, BaseTool, ToolStatus, collect_findings

PROFILES: Dict[str, Dict[str, Any]] = {
    "full": {
        "tools": ["audit_engine", "semgrep", "gitleaks", "trivy", "nuclei", "strix"],
        "fail_on": ["critical", "high"],
        "needs_target": ["nuclei", "strix"],
        "timeout": 900,
    },
    "fast": {
        "tools": ["audit_engine", "gitleaks"],
        "fail_on": ["critical", "high"],
        "needs_target": [],
        "timeout": 300,
    },
    "qa": {
        "tools": ["audit_engine", "semgrep"],
        "fail_on": ["critical"],
        "needs_target": [],
        "timeout": 600,
    },
    "pentest": {
        "tools": ["nuclei", "strix"],
        "fail_on": ["critical", "high"],
        "needs_target": ["nuclei", "strix"],
        "timeout": 1800,
    },
}


def wait_for_target(target: str, timeout_s: int = 90) -> tuple:
    """Live hədəfə /health və ya / GET sorğusu; hazır olana qədər gözləyir."""
    url = target.rstrip("/") + "/health"
    alt_url = target.rstrip("/") + "/"
    start = time.time()
    last_err = ""
    while time.time() - start < timeout_s:
        for u in (url, alt_url):
            try:
                with urllib.request.urlopen(u, timeout=5) as resp:
                    if resp.status < 400:
                        return True, u, f"HTTP {resp.status}"
            except urllib.error.HTTPError as e:
                if e.code < 500:
                    return True, u, f"HTTP {e.code}"
                last_err = f"HTTP {e.code}"
            except Exception as e:
                last_err = f"{type(e).__name__}"
        time.sleep(2)
    return False, "", f"{timeout_s}s gözləmədən sonra hədəf cavab vermədi ({last_err})"


class Pipeline:
    """Bir DevSecOps run-u: statik (paralel) + DAST (hədəflə) + gate + report.
    on_event callback: real vaxt hadisə axını (GUI/web üçün)."""

    def __init__(self, profile: str, project: Path, out_dir: Path,
                 target: Optional[str] = None, fail_on: Optional[List[str]] = None,
                 timeout: int = 900, verbose: bool = False, on_event: Optional[callable] = None):
        self.profile_name = profile
        self.profile = PROFILES[profile]
        self.project = project.resolve()
        self.out_dir = out_dir.resolve()
        self.target = target
        self.fail_on = fail_on or self.profile["fail_on"]
        self.timeout = timeout
        self.verbose = verbose
        self.tools: List[BaseTool] = []
        self._on_event = on_event or (lambda e: None)
        self._cancelled = False
        self.result: Optional[dict] = None

    def emit(self, kind: str, **data) -> None:
        """Hadisə yayımla (kind: run_start|target|log|tool_start|tool_finish|findings|gate|done)."""
        try:
            self._on_event({"kind": kind, **data})
        except Exception:
            pass  # hadisə istehlakçısı çöksə pipeline pozmur

    def cancel(self) -> None:
        """Bütün işlək subprocess-ləri öldürür."""
        self._cancelled = True
        for t in self.tools:
            t.cancel()
        self.emit("log", name="orchestrator", level="warn", line="⛔ Cancel istənildi — proseslər dayandırılır")

    @property
    def cancelled(self) -> bool:
        return self._cancelled

    def log(self, msg: str) -> None:
        print(f"[orchestrator] {msg}", flush=True)

    def _prepare_target(self) -> None:
        needs = set(self.profile["needs_target"]) & set(self.profile["tools"])
        if needs and not self.target:
            raise ValueError(f"Profil '{self.profile_name}' live hədəf tələb edir: {needs} (— --target əlavə edin)")
        if self.target:
            self.emit("log", name="orchestrator", level="info", line=f"⏳ Hədəf gözlənilir: {self.target}")
            ok, url, note = wait_for_target(self.target)
            if ok:
                self.log(f"✅ Live hədəf hazır: {url} ({note})")
                self.emit("target", ready=True, url=url, note=note)
            else:
                self.log(f"⚠️ Hədəf cavab vermədi: {note} — DAST skan buna baxmayracak çalışacaq")
                self.emit("target", ready=False, url="", note=note)

    def _build_tools(self) -> None:
        for name in self.profile["tools"]:
            cls: Type[BaseTool] = TOOL_REGISTRY[name]
            # audit_engine repo daxili Python moduludur — binary axtarılmır
            binary = "internal" if name == "audit_engine" else resolve(name)
            env = {}
            if name == "strix":
                import os
                key = os.environ.get("LLM_API_KEY", "")
                if key:
                    env["LLM_API_KEY"] = key
                if os.environ.get("STRIX_LLM"):
                    env["STRIX_LLM"] = os.environ["STRIX_LLM"]
            tool = cls(binary=binary, timeout=self.timeout, env_extra=env)
            tool.line_callback = lambda line, _n=name: self.emit(
                "log", name=_n, level="out", line=line[:400]
            )
            self.tools.append(tool)
            if not tool.available:
                self.log(f"⚠️ {name}: binary yoxdur → SKIPPED")
                self.emit("log", name="orchestrator", level="warn", line=f"⚠️ {name}: binary yoxdur → SKIPPED")

    def _run_static(self, tool: BaseTool) -> BaseTool:
        start = time.time()
        self.emit("tool_start", name=tool.name)
        self.log(f"▶ {tool.name} başlayır...")
        try:
            tool.run(self.project, self.out_dir, self.target)
        except Exception as e:  # müdafiə: tool çöksə belə pipeline davam edir
            tool.status = ToolStatus.FAILED
            tool.reason = f"unhandled: {type(e).__name__}: {e}"
        tool.duration_s = round(time.time() - start, 2)
        # Cancel səbəbindən öldürülmüş prosesləri düzgün etiketlə
        if (self._cancelled and tool.status == ToolStatus.FAILED
                and tool.exec_result is not None
                and tool.exec_result.exit_code is not None and tool.exec_result.exit_code < 0):
            tool.status = ToolStatus.CANCELLED
            tool.reason = "run ləğv edildi (Stop)"
        self.emit("tool_finish", name=tool.name, status=tool.status,
                  findings_count=len(tool.findings), duration_s=tool.duration_s,
                  reason=(tool.reason or "")[:200])
        if tool.status == ToolStatus.OK:
            self.log(f"✅ {tool.name}: {len(tool.findings)} tapıntı ({tool.duration_s}s)")
            self.emit("findings", name=tool.name, findings=tool.findings)
        elif tool.status == ToolStatus.SKIPPED:
            self.log(f"⏭️ {tool.name}: SKIPPED — {tool.reason}")
        elif tool.status in (ToolStatus.FAILED, ToolStatus.TIMEOUT):
            self.log(f"❌ {tool.name}: {tool.status} — {(tool.reason or '')[:120]}")
        else:
            self.log(f"❌ {tool.name}: {tool.status} — {(tool.reason or '')[:120]}")
        return tool

    def run(self) -> Dict[str, Any]:
        self.log(f"Profil: {self.profile_name} | Proyekt: {self.project} | Hədəf: {self.target or '—'}")
        self.emit("run_start", profile=self.profile_name, project=str(self.project),
                  target=self.target or "", fail_on=self.fail_on,
                  tools=list(self.profile["tools"]))
        self.out_dir.mkdir(parents=True, exist_ok=True)

        self._prepare_target()
        self._build_tools()

        # Statik + DAST hamısı paralel (istiqamətsiz, hər tool öz izolyasiyasında)
        started = time.time()
        with ThreadPoolExecutor(max_workers=min(6, len(self.tools) or 1)) as pool:
            futures = [pool.submit(self._run_static, t) for t in self.tools]
            for _ in as_completed(futures):
                pass

        findings = collect_findings(self.tools)
        gate = DeterministicGate(self.fail_on)
        gate_result = gate.decision(findings)

        unified = {
            "schema_version": "2.0",
            "profile": self.profile_name,
            "project": str(self.project),
            "target": self.target or "",
            "started_at": datetime_from_epoch(started),
            "tools": [self._tool_row(t) for t in self.tools],
            "findings": findings,
            "gate": gate_result,
            "deterministic": True,
            "llm_involved": any(t.name == "strix" and t.status == ToolStatus.OK for t in self.tools),
        }

        write_json(unified, self.out_dir / "unified_findings.json")
        report_path = write_markdown(unified, self.out_dir, self.fail_on)

        self.log(f"📊 Cəmi tapıntı: {len(findings)} | Gate: {gate_result['decision']}")
        self.log(f"📄 Hesabat: {report_path}")
        self.emit("gate", decision=gate_result["decision"], reason=gate_result["reason"],
                  severity_counts=gate_result["severity_counts"], blocking_count=gate_result["blocking_count"])
        self.emit("done", exit_code=0 if gate_result["passed"] else 1,
                  total_findings=len(findings), findings=findings,
                  report=str(report_path), out_dir=str(self.out_dir), cancelled=self._cancelled)

        # CLI exit code: gate qərarına bağlı (0=ALLOW, 1=BLOCK, 2=manqalıq)
        self.result = unified
        return unified

    @staticmethod
    def _tool_row(t: BaseTool) -> dict:
        return {
            "name": t.name,
            "status": t.status,
            "reason": t.reason or "",
            "findings_count": len(t.findings),
            "duration_s": getattr(t, "duration_s", 0),
            "command": (t.exec_result.command if t.exec_result else [])[:1],
            "exit_code": t.exec_result.exit_code if t.exec_result else None,
            "raw_file": _raw_file_for(t),
        }


def _raw_file_for(t: BaseTool) -> str:
    mapping = {
        "semgrep": "semgrep.json", "gitleaks": "gitleaks.json", "trivy": "trivy.json",
        "nuclei": "nuclei.jsonl", "strix": "strix.json", "audit_engine": "audit_findings.json",
    }
    name = mapping.get(t.name, "")
    return name


def datetime_from_epoch(epoch: float) -> str:
    import datetime as dt
    return dt.datetime.fromtimestamp(epoch).isoformat()
