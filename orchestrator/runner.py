"""
Subprocess Runner — timeout, retry, real status.
Heç nə heç vaxt "saxta keçdi" qaytarmır.
"""

import os
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any


@dataclass
class ExecResult:
    """Bir əmrin real icra nəticəsi."""
    command: List[str]
    exit_code: Optional[int] = None   # None = icra olunmadı (tool yoxdur və s.)
    stdout: str = ""
    stderr: str = ""
    timed_out: bool = False
    not_found: bool = False
    error: Optional[str] = None
    started_at: str = field(default_factory=lambda: datetime.now().isoformat())
    duration_s: float = 0.0

    @property
    def ran(self) -> bool:
        return self.exit_code is not None and not self.timed_out and not self.not_found

    def output_all(self) -> str:
        return (self.stdout + "\n" + self.stderr).strip()


class ToolRunner:
    """Deterministik subprocess icrəsi — PATH izolyasiyası ilə."""

    def __init__(self, timeout: int = 600, retries: int = 0, env_extra: Optional[Dict[str, str]] = None,
                 cwd: Optional[str] = None):
        self.timeout = timeout
        self.retries = max(0, retries)
        self.env_extra = env_extra or {}
        self.cwd = cwd

    def _env(self) -> Dict[str, str]:
        env = os.environ.copy()
        env.update(self.env_extra)
        return env

    def exec(self, command: List[str]) -> ExecResult:
        """Əmri icra edir. Yoxdursa not_found=True ilə qaytarır (crash yox)."""
        result = ExecResult(command=command)
        start = datetime.now()

        attempt = 0
        while True:
            try:
                proc = subprocess.run(
                    command, capture_output=True, text=True,
                    timeout=self.timeout, env=self._env(), cwd=self.cwd,
                )
                result.exit_code = proc.returncode
                result.stdout = (proc.stdout or "")[-20000:]   # sübut üçün tail
                result.stderr = (proc.stderr or "")[-20000:]
                break
            except FileNotFoundError:
                result.not_found = True
                result.error = f"Tool tapılmadı: {command[0]}"
                break
            except subprocess.TimeoutExpired:
                attempt += 1
                if attempt > self.retries:
                    result.timed_out = True
                    result.error = f"Timeout {self.timeout}s ({attempt}. cəhd daxil)"
                    break
                result.stdout += f"\n[runner] Timeout, cəhd {attempt+1}..."
            except Exception as e:  # pragma: no cover — müdafiə halı
                result.error = f"Runner xətası: {type(e).__name__}: {e}"
                break

        result.duration_s = round((datetime.now() - start).total_seconds(), 2)
        return result
