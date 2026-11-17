#!/usr/bin/env python3
"""
VibeShield Desktop — cross-platform (Windows + Linux) DevSecOps/QA/Pentest GUI.

- Dərin qara, minimal dizayn, sidebar naviqasiya
- Run: real pipeline (audit_engine, semgrep, gitleaks, trivy, nuclei, strix) canlı axın + Stop
- Results: server-avtoritet tapıntı cədvəli
- AI: tapıntıların REAL LLM analizi (OpenRouter / OpenAI / Groq / Ollama — OpenAI-uyğun)
- Settings: API açarlarının idarəsi + REAL canlı yoxlama (mock data YOXDUR)
  Açarlar repo kökü config.json-da (.gitignore) — mühit dəyişəni prioritetlidir.

İstifadə:
  python desktop_app/vibeshield_desktop.py                 # GUI
  python desktop_app/vibeshield_desktop.py --selftest      # headless REAL testlər
  python desktop_app/vibeshield_desktop.py --view results  # başlanğıc view
"""

import argparse
import json
import os
import queue
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path
from tkinter import filedialog

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
# Tool binary-ləri (semgrep, nuclei, ...) hər platformada görünsün:
_TOOLS_BIN = str(ROOT / "tools" / "bin")
if Path(_TOOLS_BIN).is_dir() and _TOOLS_BIN not in os.environ.get("PATH", ""):
    os.environ["PATH"] = _TOOLS_BIN + os.pathsep + os.environ.get("PATH", "")

import orchestrator
from orchestrator import ai_analyst, config, keycheck
from orchestrator.engine import PROFILES, Pipeline
from orchestrator.resolver import REPO_ROOT, resolve
from orchestrator.tools import TOOL_REGISTRY, ToolStatus

try:
    import customtkinter as ctk
except Exception:  # headless selftest üçün GUI asılılığı məcburi deyil
    ctk = None


# --------------------------------------------------------------------------
# PipelineController — real pipeline hadisələrini thread-ə alır, UI-yə göndərir
# --------------------------------------------------------------------------
class PipelineController:
    """Pipeline thread-i + hadisə növbəsi. UI thread-inə toxunmur (queue vasitəsilə)."""

    def __init__(self):
        self.events: "queue.Queue[dict]" = queue.Queue()
        self._lock = threading.Lock()
        self.pipeline: Pipeline | None = None
        self.state = "idle"          # idle|running|blocked|allowed|cancelled|error
        self.tools: dict = {}
        self.findings: list = []
        self.gate: dict = {}
        self.run_meta: dict = {}
        self.exit_code = None
        self.out_dir = ""
        self.report = ""
        self.last_error = ""
        self.started_at = None
        self.finished_at = None

    # ---------- run ----------
    def start(self, profile: str, project: str, target: str):
        with self._lock:
            if self.state == "running":
                return False, "Run artıq işləyir — əvvəlcə Stop edin"
        if profile not in PROFILES:
            return False, f"Naməlum profil: {profile}"
        if not Path(project).is_dir():
            return False, f"Proyekt kataloqu yoxdur: {project}"
        out_dir = REPO_ROOT / "scan_out" / Path(project).name
        self._reset_state(profile, project, target)
        th = threading.Thread(target=self._worker, args=(profile, project, target, out_dir), daemon=True)
        th.start()
        return True, ""

    def _reset_state(self, profile, project, target):
        with self._lock:
            self.state = "running"
            self.started_at = time.time()
            self.finished_at = None
            self.exit_code = None
            self.out_dir = ""
            self.report = ""
            self.last_error = ""
            self.gate = {}
            self.findings = []
            self.run_meta = {"profile": profile, "project": project, "target": target or ""}
            self.tools = {n: {"status": "pending", "findings_count": 0, "duration_s": 0, "reason": ""}
                          for n in PROFILES[profile]["tools"]}

    def _worker(self, profile, project, target, out_dir):
        try:
            p = Pipeline(profile=profile, project=Path(project), out_dir=out_dir,
                         target=target or None, on_event=self._on_event)
            with self._lock:
                self.pipeline = p
            p.run()
        except ValueError as e:
            self._on_event({"kind": "error", "message": str(e)})
        except Exception as e:  # pragma: no cover — müdafiə
            self._on_event({"kind": "error", "message": f"{type(e).__name__}: {e}"})

    def stop(self) -> bool:
        with self._lock:
            p = self.pipeline
        if p is not None and self.state == "running":
            threading.Thread(target=p.cancel, daemon=True).start()
            return True
        return False

    # ---------- hadisələr ----------
    def _on_event(self, ev: dict) -> None:
        kind = ev.get("kind")
        with self._lock:
            if kind == "tool_start":
                t = self.tools.get(ev["name"])
                if t:
                    t["status"] = "running"
            elif kind == "tool_finish":
                t = self.tools.get(ev["name"])
                if t:
                    t["status"] = str(ev.get("status", "")).lower()
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
                if ev.get("findings"):
                    self.findings = ev["findings"]          # server avtoritet siyahı
                if ev.get("cancelled"):
                    self.state = "cancelled"
                elif self.exit_code == 0:
                    self.state = "allowed"
                elif self.exit_code == 1:
                    self.state = "blocked"
                else:
                    self.state = "error"
            elif kind == "error":
                self.last_error = ev.get("message", "")
                self.state = "error"
                self.finished_at = time.time()
        self.events.put(ev)

    # ---------- snapshot / restore ----------
    def snapshot(self) -> dict:
        with self._lock:
            elapsed = None
            if self.started_at:
                elapsed = round((self.finished_at or time.time()) - self.started_at, 1)
            return {
                "state": self.state, "elapsed_s": elapsed,
                "meta": dict(self.run_meta),
                "tools": {n: dict(t) for n, t in self.tools.items()},
                "findings": list(self.findings),
                "gate": dict(self.gate),
                "exit_code": self.exit_code, "out_dir": self.out_dir,
                "report": self.report, "last_error": self.last_error,
            }

    def restore(self, path: Path) -> bool:
        """Əvvəlki run-un unified_findings.json-unu vəziyyətə yüklə (startda)."""
        try:
            data = json.loads(Path(path).read_text(encoding="utf-8"))
        except Exception:
            return False
        g = data.get("gate", {}) or {}
        exit_code = 0 if g.get("passed") else 1
        with self._lock:
            self.state = "allowed" if g.get("passed") else "blocked"
            self.exit_code = exit_code
            self.started_at = None
            self.finished_at = None
            self.out_dir = str(data.get("out_dir") or Path(path).parent)
            self.report = str(Path(path).parent / "report.md")
            self.gate = g
            self.findings = data.get("findings", [])
            self.run_meta = {"profile": data.get("profile", ""), "project": data.get("project", ""),
                             "target": data.get("target", "")}
            self.tools = {t["name"]: {"status": str(t.get("status", "")).lower(),
                                      "findings_count": t.get("findings_count", 0),
                                      "duration_s": t.get("duration_s", 0),
                                      "reason": t.get("reason", "")}
                          for t in data.get("tools", [])}
        return True

    @staticmethod
    def find_last_result() -> Path | None:
        base = REPO_ROOT / "scan_out"
        if not base.is_dir():
            return None
        cands = list(base.glob("*/unified_findings.json"))
        if not cands:
            return None
        return max(cands, key=lambda p: p.stat().st_mtime)


# --------------------------------------------------------------------------
# SELFTEST — headless, hamısı REAL: mock yoxdur
# --------------------------------------------------------------------------
def run_selftest() -> int:
    print("=" * 66)
    print("VibeShield Desktop — SELFTEST (headless · hamısı REAL icralar)")
    print("=" * 66)
    results: list = []

    def report(name: str, ok: bool, detail: str = ""):
        results.append((ok, name))
        print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))

    fake = {"llm_api_key": "sk-or-fake-0000000000000000",
            "strix_llm": "openai/gpt-4o-mini",
            "llm_api_base": "https://openrouter.ai/api/v1",
            "github_token": "ghp_fake0000000000000000000000000000"}

    # 1) config.json → engine env keçidi (real wiring)
    backup = config.CONFIG_PATH.read_bytes() if config.CONFIG_PATH.is_file() else None
    try:
        config.save_config(fake)
        p = Pipeline(profile="full", project=REPO_ROOT / "target_app",
                     out_dir=REPO_ROOT / "scan_out" / "selftest", target=None,
                     on_event=lambda e: None)
        p._build_tools()
        strix = next(t for t in p.tools if t.name == "strix")
        env = getattr(strix.runner, "env_extra", {})
        ok = (env.get("LLM_API_KEY") == fake["llm_api_key"]
              and env.get("STRIX_LLM") == fake["strix_llm"]
              and env.get("LLM_API_BASE") == fake["llm_api_base"]
              and env.get("GITHUB_TOKEN") == fake["github_token"])
        report("config.json → StrixTool env (key+model+base+GitHub)", ok,
               "env keys: " + ",".join(sorted(env)))
    except Exception as e:
        report("config.json → StrixTool env", False, f"{type(e).__name__}: {e}")
    finally:
        if backup is not None:
            config.CONFIG_PATH.write_bytes(backup)
        elif config.CONFIG_PATH.is_file():
            config.CONFIG_PATH.unlink()

    # 2) REAL canlı API yoxlama — saxta açarla endpoint real 401 qaytarmalıdır
    try:
        r = keycheck.check_llm(fake["llm_api_key"], fake["llm_api_base"], fake["strix_llm"])
        report("LLM canlı yoxlama → real OpenRouter cavabı", r["live"], r["detail"])
        report("Saxta LLM açarı REAL rədd edildi (401)", r["ok"] is False, r["detail"])
    except Exception as e:
        report("LLM canlı yoxlama", False, f"{type(e).__name__}: {e}")
    try:
        g = keycheck.check_github(fake["github_token"])
        report("GitHub canlı yoxlama → real api.github.com cavabı", g["live"], g["detail"])
        report("Saxta GitHub tokenı REAL rədd edildi", g["ok"] is False, g["detail"])
    except Exception as e:
        report("GitHub canlı yoxlama", False, f"{type(e).__name__}: {e}")

    # 3) AI analiz: açar yoxdursa REAL xəta qaytarmalıdır (mock cavab yoxdur)
    try:
        try:
            ai_analyst.analyze_findings([{"severity": "high", "tool": "x", "title": "t"}])
            report("AI analiz açarsız → AIError (mock yox)", False, "AIError qalxmadı!")
        except ai_analyst.AIError as e:
            report("AI analiz açarsız → AIError (mock yox)", True, str(e))
    except Exception as e:
        report("AI analiz açarsız", False, f"{type(e).__name__}: {e}")

    # 4) Pipeline canlı run controller üzərindən (fast profil — real tool icrası)
    project = REPO_ROOT / "target_app"
    if not project.is_dir():
        report("Pipeline canlı run (fast)", False, "target_app kataloqu yoxdur")
    else:
        c = PipelineController()
        ok, msg = c.start("fast", str(project), "")
        if not ok:
            report("Pipeline canlı run (fast)", False, msg)
        else:
            deadline = time.time() + 240
            kinds: set = set()
            while time.time() < deadline:
                try:
                    ev = c.events.get(timeout=1.0)
                    kinds.add(ev.get("kind"))
                except queue.Empty:
                    if c.state != "running":
                        break
            need = {"run_start", "tool_start", "log", "tool_finish", "gate", "done"}
            report("Pipeline canlı run (fast) — tam hadisə axını", need <= kinds,
                   f"state={c.state} · tapıntı={len(c.findings)} · gate={c.gate.get('decision')} · events={sorted(kinds)}")
            exp = 0 if (c.gate or {}).get("passed") else 1
            report("Exit kodu gate qərarı ilə uzlaşır", c.exit_code == exp, f"exit={c.exit_code}")

    print("-" * 66)
    fails = [n for ok, n in results if not ok]
    print(f"NƏTİCƏ: {len(results) - len(fails)}/{len(results)} PASS")
    for n in fails:
        print(f"  ✗ {n}")
    return 0 if not fails else 1


# --------------------------------------------------------------------------
# GUI
# --------------------------------------------------------------------------
if ctk is not None:
    ctk.set_appearance_mode("dark")
    ctk.set_widget_scaling(1.0)
    ctk.set_window_scaling(1.0)

    C = {
        "bg": "#0A0A0C", "panel": "#101013", "panel2": "#15151A", "panel3": "#1A1A20",
        "border": "#232329", "border2": "#2E2E36",
        "txt": "#F2F2F4", "mut": "#9A9AA2", "dim": "#5A5A62",
        "green": "#3FB950", "red": "#F85149",
        # sadələşdirilmiş palitra: köhnə vurğu rəngləri neytrala keçir
        "amber": "#9A9AA2", "cyan": "#F2F2F4", "violet": "#9A9AA2", "orange": "#F2F2F4",
    }
    SEV_ORDER = ["critical", "high", "medium", "low", "info"]
    SEV_COLOR = {"critical": C["red"], "high": C["txt"], "medium": C["mut"],
                 "low": C["dim"], "info": C["dim"]}
    SEV_BG = {"critical": "#221214", "high": "#1A1A20", "medium": "#1A1A20",
              "low": "#1A1A20", "info": "#1A1A20"}
    DOT = {"pending": C["dim"], "running": C["txt"], "ok": C["green"],
           "failed": C["red"], "timeout": C["red"], "skipped": C["dim"],
           "not_found": C["dim"], "cancelled": C["mut"]}
    PILL = {"idle": ("İDLE", C["dim"]), "running": ("RUNNING", C["txt"]),
            "blocked": ("BLOCKED", C["red"]), "allowed": ("ALLOW", C["green"]),
            "cancelled": ("CANCELLED", C["mut"]), "error": ("ERROR", C["red"])}
    NAV = [("dashboard", "◧  Dashboard"), ("run", "▶  Run"), ("results", "≡  Results"),
           ("ai", "✦  AI Analiz"), ("settings", "⚙  Settings")]

    def open_path(p: Path) -> None:
        try:
            if sys.platform.startswith("win"):
                os.startfile(str(p))  # type: ignore[attr-defined]
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(p)])
            else:
                subprocess.Popen(["xdg-open", str(p)])
        except Exception:
            pass

    class App(ctk.CTk):
        def __init__(self, start_view: str = "run"):
            super().__init__(fg_color=C["bg"])
            self.title("VibeShield — DevSecOps Orchestrator")
            self.geometry("1280x800")
            self.minsize(1080, 700)
            self.controller = PipelineController()

            self.f_h1 = ctk.CTkFont(size=17, weight="bold")
            self.f_h2 = ctk.CTkFont(size=14, weight="bold")
            self.f_big = ctk.CTkFont(size=27, weight="bold")
            self.f_mono = ctk.CTkFont(family="Consolas", size=12)
            self.f_mono_s = ctk.CTkFont(family="Consolas", size=11)
            self.f_s = ctk.CTkFont(size=11)

            self._build_sidebar()
            self._build_header()
            self._build_views()

            restored = False
            last = PipelineController.find_last_result()
            if last:
                restored = self.controller.restore(last)
            self._render_from_state(initial=restored)
            self.show(start_view if start_view in dict(NAV) else "run")
            self.after(90, self._drain)
            threading.Thread(target=self._tools_check_worker, daemon=True).start()

        # ---------------- sidebar ----------------
        def _build_sidebar(self):
            sb = ctk.CTkFrame(self, width=212, fg_color=C["panel"], corner_radius=0)
            sb.grid(row=0, column=0, sticky="nsw")
            sb.grid_propagate(False)
            sb.grid_rowconfigure(len(NAV) + 2, weight=1)

            logo = ctk.CTkFrame(sb, fg_color="transparent")
            logo.pack(fill="x", padx=18, pady=(22, 26))
            ctk.CTkLabel(logo, text="🛡️", font=ctk.CTkFont(size=24)).pack(anchor="w")
            ctk.CTkLabel(logo, text="VibeShield", font=self.f_h1, text_color=C["txt"]).pack(anchor="w")
            ctk.CTkLabel(logo, text="devsecops · qa · pentest", font=self.f_s,
                         text_color=C["dim"]).pack(anchor="w")

            self._nav_btns = {}
            for key, label in NAV:
                b = ctk.CTkButton(sb, text=label, anchor="w", height=38, corner_radius=8,
                                  fg_color="transparent", hover_color=C["panel3"],
                                  text_color=C["mut"], font=ctk.CTkFont(size=13),
                                  command=lambda k=key: self.show(k))
                b.pack(fill="x", padx=12, pady=2)
                self._nav_btns[key] = b

            foot = ctk.CTkFrame(sb, fg_color="transparent")
            foot.pack(side="bottom", fill="x", padx=18, pady=16)
            self.s_status = ctk.CTkLabel(foot, text="●  İDLE", font=self.f_mono_s, text_color=C["dim"])
            self.s_status.pack(anchor="w")
            ctk.CTkLabel(foot, text=f"v{orchestrator.__version__}", font=self.f_s,
                         text_color=C["dim"]).pack(anchor="w")

        # ---------------- header ----------------
        def _build_header(self):
            hd = ctk.CTkFrame(self, fg_color=C["panel"], corner_radius=0, height=56)
            hd.grid(row=0, column=1, sticky="new")
            hd.grid_columnconfigure(0, weight=1)
            self.h_title = ctk.CTkLabel(hd, text="Run", font=self.f_h1, text_color=C["txt"])
            self.h_title.grid(row=0, column=0, sticky="w", padx=24)
            self.h_clock = ctk.CTkLabel(hd, text="", font=self.f_mono, text_color=C["mut"])
            self.h_clock.grid(row=0, column=1, sticky="e", padx=8)
            self.h_pill = ctk.CTkLabel(hd, text="●  İDLE", font=self.f_mono_s, text_color=C["dim"])
            self.h_pill.grid(row=0, column=2, sticky="e", padx=24)
            self.grid_columnconfigure(1, weight=1)
            self.grid_rowconfigure(0, weight=1)

        # ---------------- views ----------------
        def _build_views(self):
            self.container = ctk.CTkFrame(self, fg_color="transparent")
            self.container.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
            self.container.grid_rowconfigure(0, weight=1)
            self.container.grid_columnconfigure(0, weight=1)
            self.views = {}
            for name in dict(NAV):
                f = ctk.CTkFrame(self.container, fg_color="transparent")
                f.grid(row=0, column=0, sticky="nsew")
                self.views[name] = f
            self._build_view_run(self.views["run"])
            self._build_view_dashboard(self.views["dashboard"])
            self._build_view_results(self.views["results"])
            self._build_view_ai(self.views["ai"])
            self._build_view_settings(self.views["settings"])

        def show(self, name: str):
            for key, b in self._nav_btns.items():
                if key == name:
                    b.configure(fg_color=C["panel3"], text_color=C["txt"],
                                border_width=1, border_color=C["border2"])
                else:
                    b.configure(fg_color="transparent", text_color=C["mut"], border_width=0)
            for key, f in self.views.items():
                f.grid_remove() if key != name else f.grid()
            self.h_title.configure(text=dict(NAV)[name].split("  ", 1)[1])
            if name == "dashboard":
                self._refresh_dashboard()
            elif name == "results":
                self._rebuild_findings()
            elif name == "ai":
                self._refresh_ai_info()
            elif name == "settings":
                self._refresh_key_hints()

        # ================= RUN VIEW =================
        def _build_view_run(self, f):
            f.grid_rowconfigure(3, weight=1)
            f.grid_columnconfigure(0, weight=1)

            ctl = ctk.CTkFrame(f, fg_color=C["panel"], corner_radius=12,
                               border_width=1, border_color=C["border"])
            ctl.grid(row=0, column=0, sticky="ew", padx=20, pady=(18, 10))
            for i, w in enumerate([150, 1, 1, 0]):
                ctl.grid_columnconfigure(i, weight=w)

            ctk.CTkLabel(ctl, text="PROFİL", font=self.f_s, text_color=C["dim"]).grid(
                row=0, column=0, sticky="w", padx=(16, 6), pady=(10, 0))
            self.r_profile = ctk.CTkOptionMenu(ctl, values=list(PROFILES.keys()), width=140,
                                               fg_color=C["panel3"], button_color=C["border2"],
                                               button_hover_color=C["border2"], text_color=C["txt"],
                                               font=self.f_mono_s)
            self.r_profile.grid(row=1, column=0, sticky="ew", padx=(16, 8), pady=(2, 12))
            ctk.CTkLabel(ctl, text="PROYEKT", font=self.f_s, text_color=C["dim"]).grid(
                row=0, column=1, sticky="w", padx=6, pady=(10, 0))
            proj = ctk.CTkFrame(ctl, fg_color="transparent")
            proj.grid(row=1, column=1, sticky="ew", padx=6, pady=(2, 12))
            proj.grid_columnconfigure(0, weight=1)
            self.r_project = ctk.CTkEntry(proj, fg_color=C["panel3"], border_color=C["border"],
                                          font=self.f_mono_s, placeholder_text="skan ediləcək kataloq")
            self.r_project.insert(0, str(REPO_ROOT / "target_app"))
            self.r_project.grid(row=0, column=0, sticky="ew")
            ctk.CTkButton(proj, text="📂", width=40, height=34, corner_radius=8,
                          fg_color=C["panel3"], hover_color=C["border2"], text_color=C["txt"],
                          command=self._browse_project).grid(row=0, column=1, padx=(6, 0))
            ctk.CTkLabel(ctl, text="HƏDƏF (DAST)", font=self.f_s, text_color=C["dim"]).grid(
                row=0, column=2, sticky="w", padx=6, pady=(10, 0))
            self.r_target = ctk.CTkEntry(ctl, fg_color=C["panel3"], border_color=C["border"],
                                         font=self.f_mono_s, placeholder_text="http://localhost:8000")
            self.r_target.grid(row=1, column=2, sticky="ew", padx=6, pady=(2, 12))
            btns = ctk.CTkFrame(ctl, fg_color="transparent")
            btns.grid(row=1, column=3, padx=(6, 14), pady=(2, 12))
            self.r_run = ctk.CTkButton(btns, text="▶  RUN", width=110, height=36, corner_radius=9,
                                       fg_color=C["green"], hover_color="#2EA043", text_color="#0A0A0C",
                                       font=ctk.CTkFont(size=13, weight="bold"), command=self._on_run)
            self.r_run.pack(side="left", padx=(0, 6))
            self.r_stop = ctk.CTkButton(btns, text="■  STOP", width=90, height=36, corner_radius=9,
                                        fg_color=C["red"], hover_color="#DA3633", text_color="#FFFFFF",
                                        font=ctk.CTkFont(size=13, weight="bold"),
                                        state="disabled", command=self._on_stop)
            self.r_stop.pack(side="left")

            tools_f = ctk.CTkFrame(f, fg_color="transparent")
            tools_f.grid(row=1, column=0, sticky="ew", padx=20)
            tools_f.grid_columnconfigure((0, 1, 2), weight=1, uniform="t")
            self.tool_cards = {}
            for i, name in enumerate(PROFILES["full"]["tools"]):
                card = ctk.CTkFrame(tools_f, fg_color=C["panel"], corner_radius=12,
                                    border_width=1, border_color=C["border"])
                card.grid(row=i // 3, column=i % 3, sticky="ew", padx=5, pady=5)
                card.grid_columnconfigure(1, weight=1)
                dot = ctk.CTkLabel(card, text="●", font=ctk.CTkFont(size=11), text_color=C["dim"], width=14)
                dot.grid(row=0, column=0, sticky="w", padx=(14, 2), pady=(12, 0))
                ctk.CTkLabel(card, text=name, font=self.f_mono_s, text_color=C["txt"]).grid(
                    row=0, column=1, sticky="w", padx=2, pady=(12, 0))
                cnt = ctk.CTkLabel(card, text="—", font=ctk.CTkFont(size=24, weight="bold"),
                                   text_color=C["dim"])
                cnt.grid(row=1, column=0, columnspan=2, sticky="w", padx=14, pady=(2, 0))
                sub = ctk.CTkLabel(card, text="gözləmədə", font=self.f_s, text_color=C["dim"], anchor="w")
                sub.grid(row=2, column=0, columnspan=2, sticky="ew", padx=14, pady=(1, 12))
                self.tool_cards[name] = {"frame": card, "dot": dot, "cnt": cnt, "sub": sub}

            self.gate_frame = ctk.CTkFrame(f, fg_color=C["panel"], corner_radius=13,
                                           border_width=1, border_color=C["border"], height=64)
            self.gate_icon = ctk.CTkLabel(self.gate_frame, text="", font=ctk.CTkFont(size=24))
            self.gate_icon.pack(side="left", padx=(18, 8), pady=10)
            gtitle = ctk.CTkFrame(self.gate_frame, fg_color="transparent")
            gtitle.pack(side="left")
            self.gate_title = ctk.CTkLabel(gtitle, text="", font=self.f_h1)
            self.gate_title.pack(anchor="w")
            self.gate_reason = ctk.CTkLabel(gtitle, text="", font=self.f_s, text_color=C["mut"])
            self.gate_reason.pack(anchor="w")
            self.gate_counts = ctk.CTkFrame(self.gate_frame, fg_color="transparent")
            self.gate_counts.pack(side="right", padx=18)
            # gizli başlayır:
            self.gate_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(10, 4))
            self.gate_frame.grid_remove()

            log_wrap = ctk.CTkFrame(f, fg_color=C["panel"], corner_radius=12,
                                    border_width=1, border_color=C["border"])
            log_wrap.grid(row=3, column=0, sticky="nsew", padx=20, pady=(10, 18))
            log_wrap.grid_rowconfigure(1, weight=1)
            log_wrap.grid_columnconfigure(0, weight=1)
            head = ctk.CTkFrame(log_wrap, fg_color="transparent")
            head.grid(row=0, column=0, sticky="ew", padx=14, pady=(10, 2))
            self.r_live = ctk.CTkLabel(head, text="● LIVE", font=self.f_s, text_color=C["dim"])
            self.r_live.pack(side="left")
            ctk.CTkLabel(head, text="  EXECUTION LOG", font=self.f_s, text_color=C["mut"]).pack(side="left")
            self.log = ctk.CTkTextbox(log_wrap, fg_color="#08080C", font=self.f_mono_s,
                                      text_color=C["txt"], wrap="none", border_width=0,
                                      scrollbar_button_color=C["border2"],
                                      scrollbar_button_hover_color=C["border2"])
            self.log.grid(row=1, column=0, sticky="nsew", padx=10, pady=(2, 10))
            self._log_tag_colors()
            self._log_line("orchestrator", "VibeShield hazırdır — Run düyməsini bas", "info")

        def _log_tag_colors(self):
            try:
                tb = self.log._textbox
                tb.tag_config("info", foreground="#B4B4BC")
                tb.tag_config("out", foreground="#C6C6CC")
                tb.tag_config("ok", foreground=C["green"])
                tb.tag_config("err", foreground=C["red"])
                tb.tag_config("warn", foreground=C["txt"])
                tb.tag_config("name", foreground="#84848C")
            except Exception:
                pass

        def _log_line(self, name: str, line: str, level: str = "out"):
            ts = time.strftime("%H:%M:%S")
            tag = {"warn": "warn", "err": "err"}.get(level, "out")
            self.log.configure(state="normal")
            self.log.insert("end", f"[{ts}] ")
            try:
                self.log._textbox.insert("end", f"[{name}] ", "name")
            except Exception:
                self.log.insert("end", f"[{name}] ")
            self.log.insert("end", line + "\n")
            try:
                self.log._textbox.tag_add(tag, "end-2lines", "end-1line")
            except Exception:
                pass
            self.log.see("end")
            self.log.configure(state="disabled")

        def _browse_project(self):
            """Fayl/kaqalog seçmə pəncərəsi — istifadəçi yazmaq əvəzinə seçir."""
            path = filedialog.askdirectory(
                parent=self, title="Skan ediləcək proyekt kataloqunu seç",
                initialdir=str(REPO_ROOT) if Path(self.r_project.get() or REPO_ROOT).exists() else str(Path.home()),
            )
            if path:
                self.r_project.delete(0, "end")
                self.r_project.insert(0, path)

        def _on_run(self):
            ok, msg = self.controller.start(self.r_profile.get(), self.r_project.get().strip(),
                                            self.r_target.get().strip())
            if not ok:
                self._log_line("orchestrator", f"✗ {msg}", "err")
                return
            self._set_running_ui(True)

        def _on_stop(self):
            if self.controller.stop():
                self._log_line("orchestrator", "⛔ Cancel göndərildi — proseslər dayandırılır", "warn")

        def _set_running_ui(self, running: bool):
            self.r_run.configure(state="disabled" if running else "normal")
            self.r_stop.configure(state="normal" if running else "disabled")
            self.r_live.configure(text="● LIVE" if running else "○ LIVE",
                                  text_color=C["cyan"] if running else C["dim"])
            if running:
                self.log.configure(state="normal")
                self.log.delete("1.0", "end")
                self.log.configure(state="disabled")
                self.gate_frame.grid_remove()
                self._clear_findings_table()
                for name in self.tool_cards:
                    self._tool_card_update(name, "pending")

        def _tool_card_update(self, name, status, n=None, dur=None, reason=""):
            card = self.tool_cards.get(name)
            if not card:
                return
            status = status.lower()
            card["dot"].configure(text_color=DOT.get(status, C["dim"]))
            card["frame"].configure(border_color=C["border"])
            if status == "running":
                card["cnt"].configure(text="·", text_color=C["cyan"])
                card["sub"].configure(text="skan işləyir...", text_color=C["cyan"])
            elif status == "pending":
                card["cnt"].configure(text="—", text_color=C["dim"])
                card["sub"].configure(text="gözləmədə", text_color=C["dim"])
            elif status == "ok":
                col = C["green"] if (n or 0) > 0 else C["mut"]
                card["cnt"].configure(text=str(n or 0), text_color=col)
                card["sub"].configure(text=f"tamamlandı · {dur or 0}s", text_color=C["dim"])
            elif status == "skipped":
                card["cnt"].configure(text="0", text_color=C["dim"])
                card["sub"].configure(text=(reason or "keçildi")[:48], text_color=C["amber"])
            elif status == "cancelled":
                card["cnt"].configure(text="0", text_color=C["dim"])
                card["sub"].configure(text="ləğv edildi", text_color=C["amber"])
            else:
                card["cnt"].configure(text="0", text_color=C["dim"])
                card["sub"].configure(text=(reason or status)[:48], text_color=C["red"])

        def _show_gate(self, gate: dict):
            decision = str(gate.get("decision", ""))
            block = decision == "BLOCK"
            self.gate_frame.grid()
            self.gate_frame.configure(border_color=C["red"] if block else C["green"])
            self.gate_icon.configure(text="🚫" if block else "✅")
            self.gate_title.configure(text="DEPLOY BLOCKED" if block else "GATE PASSED",
                                      text_color=C["red"] if block else C["green"])
            self.gate_reason.configure(text=gate.get("reason", ""))
            for w in self.gate_counts.winfo_children():
                w.destroy()
            counts = gate.get("severity_counts", {}) or {}
            for sev in SEV_ORDER:
                box = ctk.CTkFrame(self.gate_counts, fg_color=C["panel2"], corner_radius=8)
                box.pack(side="left", padx=3, pady=8)
                ctk.CTkLabel(box, text=str(counts.get(sev, 0)), font=self.f_h2,
                             text_color=SEV_COLOR[sev]).pack(padx=10, pady=(4, 0))
                ctk.CTkLabel(box, text=sev, font=self.f_s, text_color=C["dim"]).pack(padx=10, pady=(0, 4))

        # ================= DASHBOARD =================
        def _build_view_dashboard(self, f):
            f.grid_rowconfigure(2, weight=1)
            f.grid_columnconfigure(0, weight=1)
            self.d_status = ctk.CTkLabel(f, text="İDLE", font=self.f_big, text_color=C["dim"])
            self.d_status.grid(row=0, column=0, sticky="w", padx=24, pady=(22, 0))
            self.d_meta = ctk.CTkLabel(f, text="Run başlanmadı", font=self.f_s, text_color=C["mut"])
            self.d_meta.grid(row=0, column=0, sticky="s", padx=24, pady=(34, 0))

            top = ctk.CTkFrame(f, fg_color="transparent")
            top.grid(row=1, column=0, sticky="ew", padx=20, pady=(14, 8))
            top.grid_columnconfigure((0, 1, 2), weight=1, uniform="d")
            self.d_gate_card = self._dash_card(top, "GATE", 0)
            self.d_find_card = self._dash_card(top, "TAPINTI", 1)
            self.d_time_card = self._dash_card(top, "MÜDDƏT", 2)

            sev = ctk.CTkFrame(f, fg_color=C["panel"], corner_radius=12,
                               border_width=1, border_color=C["border"])
            sev.grid(row=2, column=0, sticky="nsew", padx=20, pady=(8, 18))
            sev.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(sev, text="SEVERITY PAYLANMASI", font=self.f_s,
                         text_color=C["mut"]).grid(row=0, column=0, sticky="w", padx=16, pady=(12, 4))
            self.d_sev_rows = {}
            for i, s in enumerate(SEV_ORDER):
                row = ctk.CTkFrame(sev, fg_color="transparent")
                row.grid(row=i + 1, column=0, sticky="ew", padx=16, pady=4)
                row.grid_columnconfigure(1, weight=1)
                ctk.CTkLabel(row, text=s, font=self.f_mono_s, width=80, anchor="w",
                             text_color=SEV_COLOR[s]).grid(row=0, column=0)
                bar = ctk.CTkProgressBar(row, height=9, corner_radius=5, fg_color=C["panel2"],
                                         progress_color=SEV_COLOR[s])
                bar.set(0)
                bar.grid(row=0, column=1, sticky="ew", padx=10)
                lbl = ctk.CTkLabel(row, text="0", font=self.f_mono_s, width=40, text_color=C["txt"])
                lbl.grid(row=0, column=2)
                self.d_sev_rows[s] = {"bar": bar, "lbl": lbl}
            foot = ctk.CTkFrame(sev, fg_color="transparent")
            foot.grid(row=len(SEV_ORDER) + 2, column=0, sticky="ew", padx=16, pady=(10, 12))
            self.d_report = ctk.CTkLabel(foot, text="", font=self.f_mono_s, text_color=C["dim"])
            self.d_report.pack(side="left")
            ctk.CTkButton(foot, text="📂 Hesabat qovluğu", width=140, height=30, corner_radius=8,
                          fg_color=C["panel3"], hover_color=C["border2"], text_color=C["txt"],
                          font=self.f_s, command=self._open_report_dir).pack(side="right")
            ctk.CTkButton(foot, text="✦ AI analiz", width=120, height=30, corner_radius=8,
                          fg_color=C["panel3"], hover_color=C["border2"], text_color=C["violet"],
                          font=self.f_s, command=lambda: self.show("ai")).pack(side="right", padx=8)

        def _dash_card(self, parent, title, col):
            card = ctk.CTkFrame(parent, fg_color=C["panel"], corner_radius=12,
                                border_width=1, border_color=C["border"])
            card.grid(row=0, column=col, sticky="nsew", padx=4)
            ctk.CTkLabel(card, text=title, font=self.f_s, text_color=C["dim"]).pack(anchor="w",
                                                                                    padx=16, pady=(12, 0))
            val = ctk.CTkLabel(card, text="—", font=self.f_h1, text_color=C["txt"])
            val.pack(anchor="w", padx=16, pady=(2, 12))
            return val

        def _refresh_dashboard(self):
            s = self.controller.snapshot()
            st_txt, st_col = PILL.get(s["state"], ("—", C["dim"]))
            self.d_status.configure(text=st_txt, text_color=st_col)
            m = s["meta"]
            self.d_meta.configure(text=f"profil: {m.get('profile') or '—'} · proyekt: "
                                       f"{Path(m.get('project') or '—').name} · hədəf: {m.get('target') or '—'}")
            self.d_gate_card.configure(text=str(s["gate"].get("decision", "—")) if s["gate"] else "—",
                                       text_color=C["red"] if s["gate"].get("decision") == "BLOCK" else
                                       (C["green"] if s["gate"] else C["dim"]))
            self.d_find_card.configure(text=str(len(s["findings"])), text_color=C["txt"])
            self.d_time_card.configure(text=(f"{s['elapsed_s']}s" if s["elapsed_s"] else "—"),
                                       text_color=C["txt"])
            counts = s["gate"].get("severity_counts", {}) or {}
            total = max(1, sum(counts.values()))
            for sev, row in self.d_sev_rows.items():
                n = counts.get(sev, 0)
                row["lbl"].configure(text=str(n))
                row["bar"].set(n / total)
            rep = s["report"] or (Path(s["out_dir"]) / "report.md" if s["out_dir"] else "")
            self.d_report.configure(text=str(rep) if rep else "hesabat yoxdur")

        def _open_report_dir(self):
            s = self.controller.snapshot()
            if s["out_dir"] and Path(s["out_dir"]).is_dir():
                open_path(Path(s["out_dir"]))

        # ================= RESULTS =================
        def _build_view_results(self, f):
            f.grid_rowconfigure(1, weight=1)
            f.grid_columnconfigure(0, weight=1)
            head = ctk.CTkFrame(f, fg_color="transparent")
            head.grid(row=0, column=0, sticky="ew", padx=20, pady=(18, 8))
            self.r_count = ctk.CTkLabel(head, text="0 tapıntı", font=self.f_h1, text_color=C["txt"])
            self.r_count.pack(side="left")
            ctk.CTkButton(head, text="⟳ Yenilə", width=90, height=30, corner_radius=8,
                          fg_color=C["panel3"], hover_color=C["border2"], text_color=C["txt"],
                          font=self.f_s, command=self._rebuild_findings).pack(side="right")
            wrap = ctk.CTkFrame(f, fg_color=C["panel"], corner_radius=12,
                                border_width=1, border_color=C["border"])
            wrap.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 18))
            wrap.grid_rowconfigure(0, weight=1)
            wrap.grid_columnconfigure(0, weight=1)
            self.findings_sf = ctk.CTkScrollableFrame(wrap, fg_color="#08080C", corner_radius=0,
                                                      scrollbar_button_color=C["border2"],
                                                      scrollbar_button_hover_color=C["border2"])
            self.findings_sf.grid(row=0, column=0, sticky="nsew")
            self._fkeys: set = set()

        def _clear_findings_table(self):
            for w in self.findings_sf.winfo_children():
                w.destroy()
            self._fkeys = set()

        def _finding_key(self, fd: dict) -> str:
            return "|".join(str(fd.get(k, "")) for k in ("tool", "rule_id", "title", "file", "line", "url"))

        def _add_finding_row(self, fd: dict):
            key = self._finding_key(fd)
            if key in self._fkeys:
                return
            self._fkeys.add(key)
            sev = str(fd.get("severity", "info")).lower()
            row = ctk.CTkFrame(self.findings_sf, fg_color="transparent", height=34)
            row.pack(fill="x", padx=8)
            row.grid_propagate(False)
            chip = ctk.CTkLabel(row, text=sev, font=self.f_mono_s, width=92, height=24, corner_radius=6,
                                fg_color=SEV_BG.get(sev, SEV_BG["info"]), text_color=SEV_COLOR.get(sev, C["mut"]))
            chip.pack(side="left", padx=(2, 10), pady=4)
            ctk.CTkLabel(row, text=fd.get("tool", ""), font=self.f_mono_s, width=104, anchor="w",
                         text_color=C["violet"]).pack(side="left")
            loc = fd.get("url") or (f"{fd.get('file', '')}{':' + str(fd['line']) if fd.get('line') else ''}")
            ctk.CTkLabel(row, text=fd.get("title", ""), font=self.f_mono_s, anchor="w",
                         text_color=C["txt"]).pack(side="left", fill="x", expand=True)
            ctk.CTkLabel(row, text=loc, font=self.f_mono_s, anchor="e", width=280,
                         text_color=C["dim"]).pack(side="right", padx=(8, 4))

        def _rebuild_findings(self):
            self._clear_findings_table()
            fs = sorted(self.controller.findings,
                        key=lambda x: SEV_ORDER.index(str(x.get("severity", "info")).lower())
                        if str(x.get("severity", "info")).lower() in SEV_ORDER else 9)
            for fd in fs:
                self._add_finding_row(fd)
            self.r_count.configure(text=f"{len(fs)} tapıntı")

        # ================= AI VIEW =================
        def _build_view_ai(self, f):
            f.grid_rowconfigure(2, weight=1)
            f.grid_columnconfigure(0, weight=1)
            info = ctk.CTkFrame(f, fg_color=C["panel"], corner_radius=12,
                                border_width=1, border_color=C["border"])
            info.grid(row=0, column=0, sticky="ew", padx=20, pady=(18, 10))
            info.grid_columnconfigure(0, weight=1)
            self.ai_info = ctk.CTkLabel(info, text="", font=self.f_mono_s, text_color=C["mut"],
                                        anchor="w", justify="left")
            self.ai_info.grid(row=0, column=0, sticky="ew", padx=16, pady=(10, 2))
            self.ai_findings_lbl = ctk.CTkLabel(info, text="", font=self.f_s, text_color=C["dim"],
                                                anchor="w")
            self.ai_findings_lbl.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 4))
            btns = ctk.CTkFrame(info, fg_color="transparent")
            btns.grid(row=2, column=0, sticky="ew", padx=16, pady=(2, 12))
            self.ai_btn = ctk.CTkButton(btns, text="⚡  REAL AI ANALİZ BAŞLAT", width=210, height=36,
                                        corner_radius=9, fg_color=C["txt"], hover_color="#D0D0D4",
                                        text_color="#0A0A0C", font=ctk.CTkFont(size=13, weight="bold"),
                                        command=self._ai_start)
            self.ai_btn.pack(side="left")
            self.ai_test = ctk.CTkButton(btns, text="⇄  Bağlantı Testi", width=130, height=36,
                                         corner_radius=9, fg_color=C["panel3"], hover_color=C["border2"],
                                         text_color=C["txt"], font=self.f_s, command=self._ai_conn_test)
            self.ai_test.pack(side="left", padx=8)
            self.ai_status = ctk.CTkLabel(btns, text="", font=self.f_s, text_color=C["dim"])
            self.ai_status.pack(side="left", padx=8)

            out_wrap = ctk.CTkFrame(f, fg_color=C["panel"], corner_radius=12,
                                    border_width=1, border_color=C["border"])
            out_wrap.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 18))
            out_wrap.grid_rowconfigure(1, weight=1)
            out_wrap.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(out_wrap, text="AI ÇIXIŞI (REAL API cavabı)", font=self.f_s,
                         text_color=C["mut"]).grid(row=0, column=0, sticky="w", padx=14, pady=(10, 2))
            self.ai_out = ctk.CTkTextbox(out_wrap, fg_color="#08080C", font=self.f_mono,
                                         text_color=C["txt"], wrap="word", border_width=0,
                                         scrollbar_button_color=C["border2"],
                                         scrollbar_button_hover_color=C["border2"])
            self.ai_out.grid(row=1, column=0, sticky="nsew", padx=10, pady=(2, 10))
            self.ai_out.insert("end", "AI analiz hələ icra edilməyib.\n"
                                      "Tapıntılar Settings-də yazdığın REAL API açarı ilə "
                                      "seçilmiş modelə göndərilir — mock data yoxdur.\n")
            self.ai_out.configure(state="disabled")

        def _refresh_ai_info(self):
            key = config.get_value("LLM_API_KEY")
            base = config.get_default("LLM_API_BASE")
            model = config.get_default("STRIX_LLM")
            src = "mühit" if os.environ.get("LLM_API_KEY", "").strip() else "config.json"
            if key:
                self.ai_info.configure(
                    text=f"API Key: ✓ {config.mask(key)}  ({src})\nBase: {base}\nModel: {model}",
                    text_color=C["mut"])
            else:
                self.ai_info.configure(
                    text="API Key: ✗ yoxdur — Settings-də əlavə et (OpenRouter / OpenAI / Groq / Ollama)",
                    text_color=C["red"])
            n = len(self.controller.findings)
            self.ai_findings_lbl.configure(
                text=f"Analiz üçün hazır: {n} tapıntı (son run)" if n
                else "Analiz üçün tapıntı yoxdur — əvvəlcə Run keçir")

        def _ai_start(self):
            if not self.controller.findings:
                self.ai_status.configure(text="✗ Tapıntı yoxdur — əvvəlcə Run keçir", text_color=C["amber"])
                return
            self.ai_btn.configure(state="disabled")
            self.ai_status.configure(text="⏳ REAL API sorğusu göndərilir...", text_color=C["cyan"])
            threading.Thread(target=self._ai_worker, daemon=True).start()

        def _ai_worker(self):
            try:
                text = ai_analyst.analyze_findings(self.controller.findings)
                self.controller.events.put({"kind": "ai_result", "text": text,
                                            "count": len(self.controller.findings)})
            except ai_analyst.AIError as e:
                self.controller.events.put({"kind": "ai_error", "message": str(e)})
            except Exception as e:  # pragma: no cover
                self.controller.events.put({"kind": "ai_error", "message": f"{type(e).__name__}: {e}"})

        def _ai_conn_test(self):
            self.ai_status.configure(text="⏳ Test sorğusu...", text_color=C["cyan"])
            threading.Thread(target=self._ai_test_worker, daemon=True).start()

        def _ai_test_worker(self):
            try:
                msg = ai_analyst.connection_test()
                self.controller.events.put({"kind": "ai_status_ok", "message": msg})
            except ai_analyst.AIError as e:
                self.controller.events.put({"kind": "ai_error", "message": str(e)})
            except Exception as e:
                self.controller.events.put({"kind": "ai_error", "message": f"{type(e).__name__}: {e}"})

        def _ai_result(self, ev):
            self.ai_btn.configure(state="normal")
            self.ai_status.configure(text=f"✅ {ev.get('count', 0)} tapıntı REAL analíz edildi",
                                     text_color=C["green"])
            self.ai_out.configure(state="normal")
            self.ai_out.delete("1.0", "end")
            self.ai_out.insert("end", f"─── AI Analiz · {time.strftime('%H:%M:%S')} · "
                                       f"model: {config.get_default('STRIX_LLM')} ───\n\n")
            self.ai_out.insert("end", ev.get("text", ""))
            self.ai_out.configure(state="disabled")
            self.ai_out.see("1.0")

        def _ai_error(self, ev):
            self.ai_btn.configure(state="normal")
            self.ai_status.configure(text=f"✗ {ev.get('message', 'xəta')}", text_color=C["red"])

        # ================= SETTINGS =================
        def _build_view_settings(self, f):
            wrap = ctk.CTkScrollableFrame(f, fg_color="transparent",
                                          scrollbar_button_color=C["border2"],
                                          scrollbar_button_hover_color=C["border2"])
            wrap.pack(fill="both", expand=True, padx=20, pady=(16, 14))

            note = ctk.CTkLabel(wrap, text="API açarları buradan əlavə edilir → repo kökü config.json "
                                           "(.gitignore). Prioritet: mühit dəyişəni > config.json. "
                                           "Bütün testlər REAL HTTP sorğusudur — mock yoxdur.",
                                font=self.f_s, text_color=C["mut"], anchor="w", justify="left")
            note.pack(fill="x", pady=(0, 10))

            # ---- LLM bölməsi ----
            llm = ctk.CTkFrame(wrap, fg_color=C["panel"], corner_radius=12,
                               border_width=1, border_color=C["border"])
            llm.pack(fill="x", pady=(0, 10))
            llm.grid_columnconfigure((0, 1), weight=1)
            ctk.CTkLabel(llm, text="LLM API KEY — OpenRouter / OpenAI / Groq / Ollama (OpenAI-uyğun)",
                         font=self.f_h2, text_color=C["txt"]).grid(row=0, column=0, columnspan=2,
                                                                   sticky="w", padx=16, pady=(14, 2))
            self.h_llm = ctk.CTkLabel(llm, text="", font=self.f_s, text_color=C["dim"])
            self.h_llm.grid(row=1, column=0, columnspan=2, sticky="w", padx=16)
            self.e_llm_key = ctk.CTkEntry(llm, show="●", fg_color=C["panel3"], border_color=C["border"],
                                          font=self.f_mono, placeholder_text="sk-or-v1-... (yeni açar)")
            self.e_llm_key.grid(row=2, column=0, sticky="ew", padx=16, pady=(6, 2))
            self.e_llm_base = ctk.CTkEntry(llm, fg_color=C["panel3"], border_color=C["border"],
                                           font=self.f_mono, placeholder_text="API Base (default: openrouter)")
            self.e_llm_base.insert(0, config.get_default("LLM_API_BASE"))
            self.e_llm_base.grid(row=3, column=0, sticky="ew", padx=16, pady=(2, 2))
            self.e_llm_model = ctk.CTkEntry(llm, fg_color=C["panel3"], border_color=C["border"],
                                            font=self.f_mono, placeholder_text="model (default: openai/gpt-4o-mini)")
            self.e_llm_model.insert(0, config.get_default("STRIX_LLM"))
            self.e_llm_model.grid(row=4, column=0, sticky="ew", padx=16, pady=(2, 10))
            self.s_llm = ctk.CTkLabel(llm, text="", font=self.f_s, text_color=C["dim"], anchor="w")
            self.s_llm.grid(row=5, column=0, columnspan=2, sticky="ew", padx=16, pady=(0, 2))
            brow = ctk.CTkFrame(llm, fg_color="transparent")
            brow.grid(row=6, column=0, columnspan=2, sticky="ew", padx=16, pady=(0, 14))
            ctk.CTkButton(brow, text="⚡ REAL TEST", width=120, height=32, corner_radius=8,
                          fg_color=C["panel3"], hover_color=C["border2"], text_color=C["txt"],
                          font=ctk.CTkFont(size=12, weight="bold"), command=self._test_llm).pack(side="left")
            ctk.CTkButton(brow, text="Təmizlə", width=80, height=32, corner_radius=8,
                          fg_color=C["panel3"], hover_color=C["border2"], text_color=C["mut"],
                          font=self.f_s,
                          command=lambda: self._clear_field(["llm_api_key"], self.e_llm_key)).pack(
                side="left", padx=8)

            # ---- GitHub bölməsi ----
            gh = ctk.CTkFrame(wrap, fg_color=C["panel"], corner_radius=12,
                              border_width=1, border_color=C["border"])
            gh.pack(fill="x", pady=(0, 10))
            gh.grid_columnconfigure((0, 1), weight=1)
            ctk.CTkLabel(gh, text="GITHUB TOKEN — repo / API əməliyyatları üçün (PAT)",
                         font=self.f_h2, text_color=C["txt"]).grid(row=0, column=0, columnspan=2,
                                                                   sticky="w", padx=16, pady=(14, 2))
            self.h_gh = ctk.CTkLabel(gh, text="", font=self.f_s, text_color=C["dim"])
            self.h_gh.grid(row=1, column=0, columnspan=2, sticky="w", padx=16)
            self.e_gh = ctk.CTkEntry(gh, show="●", fg_color=C["panel3"], border_color=C["border"],
                                     font=self.f_mono, placeholder_text="ghp_... / github_pat_... (yeni token)")
            self.e_gh.grid(row=2, column=0, sticky="ew", padx=16, pady=(6, 2))
            self.s_gh = ctk.CTkLabel(gh, text="", font=self.f_s, text_color=C["dim"], anchor="w")
            self.s_gh.grid(row=3, column=0, columnspan=2, sticky="ew", padx=16, pady=(0, 2))
            gbrow = ctk.CTkFrame(gh, fg_color="transparent")
            gbrow.grid(row=4, column=0, columnspan=2, sticky="ew", padx=16, pady=(0, 14))
            ctk.CTkButton(gbrow, text="⚡ REAL TEST", width=120, height=32, corner_radius=8,
                          fg_color=C["panel3"], hover_color=C["border2"], text_color=C["txt"],
                          font=ctk.CTkFont(size=12, weight="bold"), command=self._test_gh).pack(side="left")
            ctk.CTkButton(gbrow, text="Təmizlə", width=80, height=32, corner_radius=8,
                          fg_color=C["panel3"], hover_color=C["border2"], text_color=C["mut"],
                          font=self.f_s, command=lambda: self._clear_field(["github_token"], self.e_gh)).pack(
                side="left", padx=8)

            # ---- Yadda saxla ----
            save = ctk.CTkFrame(wrap, fg_color="transparent")
            save.pack(fill="x", pady=(0, 10))
            ctk.CTkButton(save, text="💾  YADDA SAXLA", width=170, height=38, corner_radius=9,
                          fg_color=C["green"], hover_color="#2EA043", text_color="#0A0A0C",
                          font=ctk.CTkFont(size=13, weight="bold"), command=self._save_settings).pack(
                side="left")
            self.s_save = ctk.CTkLabel(save, text="", font=self.f_s, text_color=C["green"])
            self.s_save.pack(side="left", padx=12)

            # ---- Tool vəziyyəti (real) ----
            tv = ctk.CTkFrame(wrap, fg_color=C["panel"], corner_radius=12,
                              border_width=1, border_color=C["border"])
            tv.pack(fill="x", pady=(0, 10))
            ctk.CTkLabel(tv, text="TOOL VƏZİYYƏTİ (real binary yoxlanışı)", font=self.f_h2,
                         text_color=C["txt"]).pack(anchor="w", padx=16, pady=(14, 4))
            self.tools_grid = ctk.CTkFrame(tv, fg_color="transparent")
            self.tools_grid.pack(fill="x", padx=16, pady=(0, 14))
            self._tools_status: dict = {}

        def _refresh_key_hints(self):
            k = config.get_value("LLM_API_KEY")
            src = "mühit dəyişənindən" if os.environ.get("LLM_API_KEY", "").strip() else "config.json-dan"
            self.h_llm.configure(text=("cari: ✓ " + config.mask(k) + f"  ({src})") if k
                                 else "cari: ✗ yoxdur")
            g = config.get_value("GITHUB_TOKEN")
            gsrc = "mühit dəyişənindən" if os.environ.get("GITHUB_TOKEN", "").strip() else "config.json-dan"
            self.h_gh.configure(text=("cari: ✓ " + config.mask(g) + f"  ({gsrc})") if g
                                else "cari: ✗ yoxdur")

        def _save_settings(self):
            patch = {}
            if (v := self.e_llm_key.get().strip()):
                patch["llm_api_key"] = v
            if (v := self.e_llm_base.get().strip()):
                patch["llm_api_base"] = v
            if (v := self.e_llm_model.get().strip()):
                patch["strix_llm"] = v
            if (v := self.e_gh.get().strip()):
                patch["github_token"] = v
            config.save_config(patch)
            self.e_llm_key.delete(0, "end")
            self.e_gh.delete(0, "end")
            self._refresh_key_hints()
            self._refresh_ai_info()
            self.s_save.configure(text="✓ yadda saxlanıldı — config.json", text_color=C["green"])

        def _clear_field(self, names, entry):
            config.delete_keys(names)
            entry.delete(0, "end")
            self._refresh_key_hints()
            self.s_save.configure(text="sahə təmizləndi", text_color=C["amber"])

        def _test_llm(self):
            self.s_llm.configure(text="⏳ REAL sorğu göndərilir...", text_color=C["cyan"])
            key = self.e_llm_key.get().strip() or config.get_value("LLM_API_KEY")
            base = self.e_llm_base.get().strip() or config.get_default("LLM_API_BASE")
            model = self.e_llm_model.get().strip() or config.get_default("STRIX_LLM")
            threading.Thread(target=self._test_llm_worker, args=(key, base, model), daemon=True).start()

        def _test_llm_worker(self, key, base, model):
            r = keycheck.check_llm(key, base, model)
            tag = "ok" if r["ok"] else "err"
            icon = "✅" if r["ok"] else "✗"
            self.controller.events.put({"kind": "settings_result", "target": "llm", "ok": r["ok"],
                                        "text": f"{icon} {r['detail']}", "live": r["live"]})

        def _test_gh(self):
            self.s_gh.configure(text="⏳ REAL sorğu göndərilir...", text_color=C["cyan"])
            tok = self.e_gh.get().strip() or config.get_value("GITHUB_TOKEN")
            threading.Thread(target=self._test_gh_worker, args=(tok,), daemon=True).start()

        def _test_gh_worker(self, tok):
            r = keycheck.check_github(tok)
            self.controller.events.put({"kind": "settings_result", "target": "gh", "ok": r["ok"],
                                        "text": f"{'✅' if r['ok'] else '✗'} {r['detail']}",
                                        "live": r["live"]})

        def _tools_check_worker(self):
            rows = []
            for n in PROFILES["full"]["tools"]:
                if n == "audit_engine":
                    rows.append((n, "OK", "daxili Python modul"))
                    continue
                p = resolve(n)
                rows.append((n, "OK" if p else "YOX", (p or "binary tapılmadı → SKIPPED")))
            docker = shutil.which("docker")
            rows.append(("docker", "OK" if docker else "YOX",
                         "strix AI agent üçün tələb" if not docker else "strix agent hazır"))
            self.controller.events.put({"kind": "tools_check", "rows": rows})

        # ---------------- hadisə dranı ----------------
        def _drain(self):
            for _ in range(250):
                try:
                    ev = self.controller.events.get_nowait()
                except queue.Empty:
                    break
                self._on_event(ev)
            self._update_clock()
            self.after(90, self._drain)

        def _update_clock(self):
            s = self.controller.snapshot()
            if s["state"] == "running" and s["elapsed_s"] is not None:
                e = s["elapsed_s"]
                self.h_clock.configure(text=f"{int(e // 60):02d}:{e % 60:04.1f}")
            self._set_pill(s["state"])

        def _set_pill(self, state):
            txt, col = PILL.get(state, ("İDLE", C["dim"]))
            self.h_pill.configure(text=f"●  {txt}", text_color=col)
            self.s_status.configure(text=f"●  {txt}", text_color=col)

        def _on_event(self, ev: dict):
            kind = ev.get("kind")
            if kind == "run_start":
                self._set_running_ui(True)
                self._log_line("orchestrator", f"Run başladı — profil={ev.get('profile')} "
                                               f"proyekt={ev.get('project')}", "info")
                if ev.get("target"):
                    self._log_line("orchestrator", f"DAST hədəfi: {ev.get('target')}", "info")
            elif kind == "target":
                if ev.get("ready"):
                    self._log_line("target", f"Hədəf hazır: {ev.get('url')} ({ev.get('note')})", "ok")
                else:
                    self._log_line("target", f"Hədəf cavab vermədi: {ev.get('note')}", "warn")
            elif kind == "tool_start":
                self._tool_card_update(ev["name"], "running")
                self._log_line(ev["name"], "başlayır", "info")
            elif kind == "tool_finish":
                st = str(ev.get("status", "")).lower()
                self._tool_card_update(ev["name"], st, ev.get("findings_count", 0),
                                       ev.get("duration_s", 0), ev.get("reason", ""))
                n = ev.get("findings_count", 0)
                if st == "ok":
                    self._log_line(ev["name"], f"{n} tapıntı ({ev.get('duration_s')}s)", "ok")
                elif st == "skipped":
                    self._log_line(ev["name"], f"SKIPPED — {ev.get('reason')}", "warn")
                elif st == "cancelled":
                    self._log_line(ev["name"], "CANCELLED", "warn")
                else:
                    self._log_line(ev["name"], f"{st} — {ev.get('reason')}", "err")
            elif kind == "findings":
                for fd in ev.get("findings", []):
                    self._add_finding_row(fd)
            elif kind == "log":
                self._log_line(ev.get("name", "orchestrator"), ev.get("line", ""),
                               ev.get("level", "out"))
            elif kind == "gate":
                self._show_gate(ev)
            elif kind == "done":
                self._set_running_ui(False)
                state = self.controller.state
                if state == "cancelled":
                    self._log_line("orchestrator", "⛔ Run ləğv olundu", "warn")
                elif state == "allowed":
                    self._log_line("gate", "✅ KEÇDİ — deploy icazəsi", "ok")
                else:
                    self._log_line("gate", "🚫 BLOKLANDI — exit 1", "err")
                # server-avtoritet yekun render
                self._rebuild_findings()
                snap = self.controller.snapshot()
                for name, t in snap["tools"].items():
                    self._tool_card_update(name, t["status"], t["findings_count"],
                                           t["duration_s"], t["reason"])
                if snap["gate"]:
                    self._show_gate(snap["gate"])
                self.h_clock.configure(
                    text=f"{int((snap['elapsed_s'] or 0) // 60):02d}:{(snap['elapsed_s'] or 0) % 60:04.1f}")
            elif kind == "error":
                self._set_running_ui(False)
                self._log_line("orchestrator", f"Xəta: {ev.get('message')}", "err")
            elif kind == "ai_result":
                self._ai_result(ev)
            elif kind == "ai_error":
                self._ai_error(ev)
            elif kind in ("ai_status_ok", "ai_status"):
                self.ai_status.configure(text=f"✅ {ev.get('message')}", text_color=C["green"])
            elif kind == "settings_result":
                lbl = self.s_llm if ev.get("target") == "llm" else self.s_gh
                lbl.configure(text=ev.get("text", ""), text_color=C["green"] if ev.get("ok") else C["red"])
            elif kind == "tools_check":
                self._render_tools_status(ev.get("rows", []))

        def _render_tools_status(self, rows):
            for w in self.tools_grid.winfo_children():
                w.destroy()
            for i, (name, st, detail) in enumerate(rows):
                row = ctk.CTkFrame(self.tools_grid, fg_color="transparent")
                row.pack(fill="x", pady=2)
                ctk.CTkLabel(row, text="●" if st == "OK" else "○", width=16,
                             text_color=C["green"] if st == "OK" else C["red"]).pack(side="left")
                ctk.CTkLabel(row, text=name, font=self.f_mono_s, width=130, anchor="w",
                             text_color=C["txt"]).pack(side="left")
                ctk.CTkLabel(row, text=detail, font=self.f_s, anchor="w", text_color=C["dim"]).pack(
                    side="left", fill="x", expand=True)

        def _render_from_state(self, initial: bool = False):
            """Restore olunmuş vəziyyəti UI-yə əks etdir (startda)."""
            snap = self.controller.snapshot()
            for name, t in snap["tools"].items():
                if name in self.tool_cards:
                    self._tool_card_update(name, t["status"] or "pending",
                                           t["findings_count"], t["duration_s"], t["reason"])
            if snap["findings"]:
                self._rebuild_findings()
            if snap["gate"]:
                self._show_gate(snap["gate"])
            if snap["meta"].get("profile"):
                m = snap["meta"]
                self.d_meta.configure(text=f"profil: {m['profile']} · proyekt: "
                                           f"{Path(m.get('project') or '—').name} · hədəf: {m.get('target') or '—'}")
            if initial and snap["out_dir"]:
                self._log_line("orchestrator", f"Əvvəlki run bərpa edildi: {snap['out_dir']}", "info")


def main() -> int:
    ap = argparse.ArgumentParser(prog="vibeshield-desktop")
    ap.add_argument("--selftest", action="store_true", help="headless REAL testlər (GUI yox)")
    ap.add_argument("--view", default="run",
                    choices=["dashboard", "run", "results", "ai", "settings"],
                    help="başlanğıc view")
    args = ap.parse_args()
    if args.selftest:
        return run_selftest()
    if ctk is None:
        print("customtkinter quraşdırılmayıb →  pip install customtkinter", file=sys.stderr)
        return 2
    app = App(start_view=args.view)
    app.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
