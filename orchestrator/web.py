#!/usr/bin/env python3
"""
VibeShield Web Dashboard — canlı orkestrasiya izləmə GUI.
Stdlib-only: ThreadingHTTPServer + Server-Sent Events (SSE).

İstifadə:
  python -m orchestrator.web                 # http://127.0.0.1:8899
  python -m orchestrator.web --port 3000 --open
API:
  GET  /              dashboard (dərin qara)
  GET  /api/state     cari vəziyyət JSON
  GET  /api/events    canlı hadisə axını (SSE)
  POST /api/run       {profile, project, target} → yeni run
  POST /api/stop      işlək run-u ləğv et
"""

import json
import queue
import shutil
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from .engine import PROFILES, Pipeline
from .resolver import REPO_ROOT
from . import __version__

DASHBOARD_HTML = Path(__file__).resolve().parent / "dashboard.html"

TOOL_ICONS = {"audit_engine": "🧬", "semgrep": "🔎", "gitleaks": "🔑",
              "trivy": "📦", "nuclei": "🎯", "strix": "🤖"}


class AppState:
    """Server tərəfli tək-run vəziyyəti (thread-safe)."""

    def __init__(self):
        self.lock = threading.Lock()
        self.status = "idle"            # idle|running|finished|blocked|cancelled
        self.run_started_at = None
        self.finished_at = None
        self.pipeline = None
        self.profile = ""
        self.project = ""
        self.target = ""
        self.tools: dict = {}           # name → {status, findings_count, duration_s, reason}
        self.findings: list = []
        self.gate: dict = {}
        self.out_dir = ""
        self.report = ""
        self.exit_code = None
        self.clients: list[queue.Queue] = []
        self.last_error = ""

    # ---------- SSE ----------
    def subscribe(self) -> queue.Queue:
        q: queue.Queue = queue.Queue(maxsize=2000)
        with self.lock:
            self.clients.append(q)
        return q

    def unsubscribe(self, q: queue.Queue) -> None:
        with self.lock:
            if q in self.clients:
                self.clients.remove(q)

    def broadcast(self, event: dict) -> None:
        with self.lock:
            clients = list(self.clients)
        for q in clients:
            try:
                q.put_nowait(event)
            except queue.Full:
                pass

    # ---------- Run ----------
    def reset_for_run(self, profile, project, target):
        with self.lock:
            self.status = "running"
            self.run_started_at = time.time()
            self.finished_at = None
            self.profile = profile
            self.project = project
            self.target = target or ""
            self.tools = {n: {"status": "pending", "findings_count": 0,
                              "duration_s": 0, "reason": ""} for n in PROFILES[profile]["tools"]}
            self.findings = []
            self.gate = {}
            self.out_dir = ""
            self.report = ""
            self.exit_code = None
            self.last_error = ""

    def handle_event(self, ev: dict) -> None:
        kind = ev.get("kind")
        with self.lock:
            if kind == "run_start":
                pass
            elif kind == "tool_start":
                self.tools[ev["name"]]["status"] = "running"
            elif kind == "tool_finish":
                t = self.tools.get(ev["name"])
                if t:
                    t["status"] = ev["status"].lower()
                    t["findings_count"] = ev.get("findings_count", 0)
                    t["duration_s"] = ev.get("duration_s", 0)
                    t["reason"] = ev.get("reason", "")
            elif kind == "findings":
                self.findings.extend(ev.get("findings", []))
            elif kind == "gate":
                self.gate = ev
            elif kind == "done":
                self.finished_at = time.time()
                self.exit_code = ev.get("exit_code")
                self.out_dir = ev.get("out_dir", "")
                self.report = ev.get("report", "")
                if ev.get("cancelled"):
                    self.status = "cancelled"
                elif self.exit_code == 0:
                    self.status = "allowed"
                elif self.exit_code == 1:
                    self.status = "blocked"
                else:
                    self.status = "finished"
            elif kind == "error":
                self.last_error = ev.get("message", "")
                self.status = "error"
                self.finished_at = time.time()
        self.broadcast(ev)

    def snapshot(self) -> dict:
        with self.lock:
            elapsed = None
            if self.run_started_at:
                elapsed = round((self.finished_at or time.time()) - self.run_started_at, 1)
            return {
                "status": self.status,
                "elapsed_s": elapsed,
                "profile": self.profile,
                "project": self.project,
                "target": self.target,
                "tools": {n: dict(t) for n, t in self.tools.items()},
                "findings": list(self.findings),
                "gate": dict(self.gate),
                "out_dir": self.out_dir,
                "report": self.report,
                "exit_code": self.exit_code,
                "last_error": self.last_error,
                "version": __version__,
                "defaults": {
                    "project": str(REPO_ROOT / "target_app"),
                    "target": "http://localhost:8000",
                    "profiles": list(PROFILES.keys()),
                },
            }


STATE = AppState()


def _run_worker(profile, project, target):
    try:
        p = Pipeline(profile=profile, project=Path(project), out_dir=REPO_ROOT / "scan_out" / Path(project).name,
                     target=target or None, on_event=STATE.handle_event)
        STATE.pipeline = p
        p.run()
    except ValueError as e:
        STATE.handle_event({"kind": "error", "message": str(e)})
    except Exception as e:
        STATE.handle_event({"kind": "error", "message": f"{type(e).__name__}: {e}"})


class Handler(BaseHTTPRequestHandler):
    server_version = "VibeShield/" + __version__

    # ---------- helpers ----------
    def _json(self, code: int, obj: dict) -> None:
        body = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self) -> dict:
        n = int(self.headers.get("Content-Length") or 0)
        if n <= 0:
            return {}
        try:
            return json.loads(self.rfile.read(n).decode())
        except Exception:
            return {}

    def log_message(self, *a):  # səssiz
        pass

    # ---------- GET ----------
    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            body = DASHBOARD_HTML.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path == "/api/state":
            self._json(200, STATE.snapshot())
        elif self.path == "/api/events":
            self._sse()
        else:
            self._json(404, {"error": "not found"})

    def _sse(self):
        q = STATE.subscribe()
        try:
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.end_headers()
            # ilk snapshot göndər
            snap = {"kind": "state", **STATE.snapshot()}
            self.wfile.write(f"data: {json.dumps(snap, ensure_ascii=False)}\n\n".encode())
            self.wfile.flush()
            while True:
                try:
                    ev = q.get(timeout=15)
                    self.wfile.write(f"data: {json.dumps(ev, ensure_ascii=False)}\n\n".encode())
                    self.wfile.flush()
                except queue.Empty:
                    self.wfile.write(b": heartbeat\n\n")   # bağlantını canlı saxla
                    self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            pass
        finally:
            STATE.unsubscribe(q)

    # ---------- POST ----------
    def do_POST(self):
        if self.path == "/api/run":
            if STATE.status == "running":
                self._json(409, {"error": "run artıq işləyir — əvvəlcə Stop edin"})
                return
            body = self._read_body()
            profile = body.get("profile", "full")
            project = body.get("project") or str(REPO_ROOT / "target_app")
            target = (body.get("target") or "").strip()
            if profile not in PROFILES:
                self._json(400, {"error": f"bilmədiyim profil: {profile}", "profiles": list(PROFILES)})
                return
            if not Path(project).is_dir():
                self._json(400, {"error": f"proyekt kataloqu yoxdur: {project}"})
                return
            STATE.reset_for_run(profile, str(Path(project).resolve()), target)
            threading.Thread(target=_run_worker, args=(profile, project, target), daemon=True).start()
            self._json(200, {"ok": True, "profile": profile, "project": project})
        elif self.path == "/api/stop":
            p = STATE.pipeline
            if p is not None and STATE.status == "running":
                threading.Thread(target=p.cancel, daemon=True).start()
                self._json(200, {"ok": True, "msg": "cancel siqnalı göndərildi"})
            else:
                self._json(200, {"ok": False, "msg": "işlək run yoxdur"})
        else:
            self._json(404, {"error": "not found"})


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser(prog="vibeshield-dashboard")
    ap.add_argument("--port", type=int, default=8899)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--open", action="store_true", help="brauzerdə avtomatik aç")
    args = ap.parse_args()

    url = f"http://{args.host}:{args.port}"
    print(f"🛡️  VibeShield Dashboard {__version__} → {url}")
    if not shutil.which("docker"):
        print("   ℹ️  docker yoxdur — strix AI pentest SKIPPED keçəcək")
    if args.open:
        import webbrowser
        webbrowser.open(url)
    srv = ThreadingHTTPServer((args.host, args.port), Handler)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nDashboard bağlandı.")


if __name__ == "__main__":
    main()
