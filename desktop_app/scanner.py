"""
DevSecOps Desktop Tool — Scanner Module
Local scans: Strix (OpenRouter), Nuclei, Semgrep, Trivy, Gitleaks
"""

import json
import os
import subprocess
import shutil
from typing import Dict, List, Optional, Any
from datetime import datetime


class ScanResult:
    def __init__(self, tool: str, success: bool, output: str, file: Optional[str] = None, error: Optional[str] = None):
        self.tool = tool
        self.success = success
        self.output = output
        self.file = file
        self.error = error
        self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tool": self.tool,
            "success": self.success,
            "output": self.output,
            "file": self.file,
            "error": self.error,
            "timestamp": self.timestamp,
        }


class DesktopScanner:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.paths = config.get("paths", {})
        self.tools = config.get("tools", {})
        self.results: List[ScanResult] = []

    def _run_cmd(self, cmd: List[str], cwd: Optional[str] = None, env: Optional[Dict[str, str]] = None) -> subprocess.CompletedProcess:
        full_env = os.environ.copy()
        if env:
            full_env.update(env)
        return subprocess.run(cmd, cwd=cwd, env=full_env, capture_output=True, text=True, timeout=300)

    def run_strix(self, api_key: str, model: str, base_url: str, target: str) -> ScanResult:
        """Strix AI pentest via OpenRouter"""
        if not shutil.which("strix"):
            return ScanResult("strix", False, "", error="strix CLI not installed. Run: curl -sSL https://strix.ai/install | bash")

        env = {
            "STRIX_LLM": model,
            "LLM_API_KEY": api_key,
            "LLM_API_BASE": base_url,
        }

        instruction = (
            "Focus ONLY on IDOR, auth bypass, secret exposure. "
            "Test auth matrix: no token, user A, user B. "
            "Report ONLY PoC-validated findings."
        )

        cmd = [
            "strix", "-n",
            "--target", target,
            "--instruction", instruction,
            "--scan-mode", self.config.get("scan_mode", "quick"),
            "--fail-on", self.config.get("fail_on", "high"),
            "--output", self.paths.get("findings_json", "findings.json"),
        ]

        try:
            proc = self._run_cmd(cmd, env=env)
            output_file = self.paths.get("findings_json", "findings.json")
            return ScanResult(
                tool="strix",
                success=proc.returncode == 0,
                output=proc.stdout + proc.stderr,
                file=output_file if os.path.exists(output_file) else None,
                error=None if proc.returncode == 0 else f"exit code {proc.returncode}",
            )
        except subprocess.TimeoutExpired:
            return ScanResult("strix", False, "", error="Strix scan timed out (300s)")
        except Exception as e:
            return ScanResult("strix", False, "", error=str(e))

    def run_nuclei(self, target: str) -> ScanResult:
        """Nuclei fallback scan (no LLM)"""
        if not shutil.which("nuclei"):
            return ScanResult("nuclei", False, "", error="nuclei CLI not installed")

        output_file = self.paths.get("nuclei_json", "nuclei.json")
        cmd = [
            "nuclei",
            "-target", target,
            "-json", "-o", output_file,
            "-severity", "high,critical",
            "-timeout", "10",
        ]

        try:
            proc = self._run_cmd(cmd)
            return ScanResult(
                tool="nuclei",
                success=proc.returncode in (0, 1),  # nuclei returns 1 if findings found
                output=proc.stdout + proc.stderr,
                file=output_file if os.path.exists(output_file) else None,
                error=None if proc.returncode in (0, 1) else f"exit code {proc.returncode}",
            )
        except Exception as e:
            return ScanResult("nuclei", False, "", error=str(e))

    def run_semgrep(self) -> ScanResult:
        """Semgrep SAST scan"""
        if not shutil.which("semgrep"):
            return ScanResult("semgrep", False, "", error="semgrep CLI not installed. Run: pip install semgrep")

        output_file = self.paths.get("semgrep_json", "semgrep.json")
        cmd = [
            "semgrep",
            "--config=auto",
            "--error",
            "--json", "--output", output_file,
            ".",
        ]

        try:
            proc = self._run_cmd(cmd)
            return ScanResult(
                tool="semgrep",
                success=proc.returncode in (0, 1),
                output=proc.stdout + proc.stderr,
                file=output_file if os.path.exists(output_file) else None,
                error=None if proc.returncode in (0, 1) else f"exit code {proc.returncode}",
            )
        except Exception as e:
            return ScanResult("semgrep", False, "", error=str(e))

    def run_trivy(self) -> ScanResult:
        """Trivy SCA scan"""
        if not shutil.which("trivy"):
            return ScanResult("trivy", False, "", error="trivy CLI not installed")

        output_file = self.paths.get("trivy_json", "trivy.json")
        cmd = [
            "trivy", "fs",
            "--severity", "CRITICAL,HIGH",
            "--format", "json",
            "--output", output_file,
            ".",
        ]

        try:
            proc = self._run_cmd(cmd)
            return ScanResult(
                tool="trivy",
                success=proc.returncode in (0, 1),
                output=proc.stdout + proc.stderr,
                file=output_file if os.path.exists(output_file) else None,
                error=None if proc.returncode in (0, 1) else f"exit code {proc.returncode}",
            )
        except Exception as e:
            return ScanResult("trivy", False, "", error=str(e))

    def run_gitleaks(self) -> ScanResult:
        """Gitleaks secrets scan"""
        if not shutil.which("gitleaks"):
            return ScanResult("gitleaks", False, "", error="gitleaks CLI not installed")

        cmd = ["gitleaks", "detect", "--source", ".", "--report-format", "json"]

        try:
            proc = self._run_cmd(cmd)
            return ScanResult(
                tool="gitleaks",
                success=proc.returncode in (0, 1),
                output=proc.stdout + proc.stderr,
                error=None if proc.returncode in (0, 1) else f"exit code {proc.returncode}",
            )
        except Exception as e:
            return ScanResult("gitleaks", False, "", error=str(e))

    def run_all_local(self, api_key: str = "", target: str = "http://localhost:8000") -> List[ScanResult]:
        """Run all enabled local scans"""
        self.results = []

        model = self.config.get("openrouter_model", "openrouter/google/gemma-2-9b-it")
        base_url = self.config.get("openrouter_base", "https://openrouter.ai/api/v1")

        if self.tools.get("strix", True):
            self.results.append(self.run_strix(api_key, model, base_url, target))

        if self.tools.get("nuclei", False):
            self.results.append(self.run_nuclei(target))

        if self.tools.get("semgrep", True):
            self.results.append(self.run_semgrep())

        if self.tools.get("trivy", True):
            self.results.append(self.run_trivy())

        if self.tools.get("gitleaks", True):
            self.results.append(self.run_gitleaks())

        return self.results

    def get_results(self) -> List[Dict[str, Any]]:
        return [r.to_dict() for r in self.results]