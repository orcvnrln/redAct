"""
Subprocess Runner — timeout, retry, canlı sətir axını, cancel.
Heç nə heç vaxt "saxta keçdi" qaytarmır.
"""

import os
import subprocess
import threading
import time as _time
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any, Callable


@dataclass
class ExecResult:
    """Bir əmrin real icra nəticəsi."""
    command: List[str]
    exit_code: Optional[int] = None   # None = icra olunmadı (tool yoxdur və s.)
    stdout: str = ""
    stderr: str = ""
    timed_out: bool = False
    not_found: bool = False
    cancelled: bool = False
    error: Optional[str] = None
    started_at: str = field(default_factory=lambda: datetime.now().isoformat())
    duration_s: float = 0.0

    @property
    def ran(self) -> bool:
        return self.exit_code is not None and not self.timed_out and not self.not_found

    def output_all(self) -> str:
        return (self.stdout + "\n" + self.stderr).strip()


class ToolRunner:
    """Deterministik subprocess icrəsi — canlı sətir callback + cancel dəstəyi."""

    def __init__(self, timeout: int = 600, retries: int = 0, env_extra: Optional[Dict[str, str]] = None,
                 cwd: Optional[str] = None):
        self.timeout = timeout
        self.retries = max(0, retries)
        self.env_extra = env_extra or {}
        self.cwd = cwd
        self._proc: Optional[subprocess.Popen] = None
        self._lock = threading.Lock()

    def _env(self) -> Dict[str, str]:
        env = os.environ.copy()
        env.update(self.env_extra)
        return env

    def exec(self, command: List[str], on_line: Optional[Callable[[str], None]] = None) -> ExecResult:
        """Əmri icra edir; hər çıxış sətri on_line callback-inə canlı gedir.
        Yoxdursa not_found=True ilə qaytarır (crash yox)."""
        result = ExecResult(command=command)
        start = datetime.now()
        attempt = 0

        while True:
            attempt += 1
            proc = None
            try:
                proc = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    text=True, bufsize=1,
                    env=self._env(), cwd=self.cwd,
                )
                with self._lock:
                    self._proc = proc

                out: List[str] = []
                deadline = _time.time() + self.timeout
                for line in proc.stdout:          # canlı axın
                    out.append(line)
                    if on_line:
                        try:
                            on_line(line.rstrip("\n"))
                        except Exception:
                            pass                    # callback çökməsi icranı öldürmür
                    if _time.time() > deadline:
                        proc.kill()
                        raise subprocess.TimeoutExpired(cmd=command, timeout=self.timeout)

                result.exit_code = proc.wait()
                result.stdout = "".join(out)[-20000:]
                break
            except FileNotFoundError:
                result.not_found = True
                result.error = f"Tool tapılmadı: {command[0]}"
                break
            except subprocess.TimeoutExpired:
                if attempt > self.retries:
                    result.timed_out = True
                    result.error = f"Timeout {self.timeout}s ({attempt}. cəhd daxil)"
                    break
                result.stdout += f"\n[runner] Timeout — cəhd {attempt + 1}..."
            except Exception as e:  # pragma: no cover — müdafiə halı
                result.error = f"Runner xətası: {type(e).__name__}: {e}"
                break
            finally:
                if proc is not None and proc.poll() is None:
                    proc.kill()
                with self._lock:
                    self._proc = None

        result.duration_s = round((datetime.now() - start).total_seconds(), 2)
        return result

    def cancel(self) -> bool:
        """İşlək prosesi öldürür (GUI Stop düyməsi)."""
        with self._lock:
            p = self._proc
        if p is not None and p.poll() is None:
            try:
                p.kill()
                return True
            except Exception:
                return False
        return False
