#!/usr/bin/env python3
"""
VibeShield Orchestrator CLI — tam avtonom DevSecOps/QA/Pentest.

İstifadə:
  python -m orchestrator.cli run --project ./target_app --target http://localhost:8000 --profile full
  python -m orchestrator.cli run --project ./myapp --profile fast
  python -m orchestrator.cli tools            # tool status cədvəli
  python -m orchestrator.cli doctor           # mühit diaqnostikası
"""

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))   # repo root → import audit.*

from orchestrator.engine import PROFILES, Pipeline            # noqa: E402
from orchestrator.resolver import resolve, REPO_ROOT          # noqa: E402
from orchestrator.tools import TOOL_REGISTRY                  # noqa: E402

EXIT_ALLOW = 0
EXIT_BLOCK = 1
EXIT_SETUP = 2


def cmd_tools(_args) -> int:
    rows = []
    for name in ["audit_engine", "semgrep", "gitleaks", "trivy", "nuclei", "strix"]:
        b = resolve(name) if name != "audit_engine" else "python (repo daxili)"
        rows.append((name, b or "YOK"))
    w = max(len(n) for n, _ in rows)
    for name, b in rows:
        print(f"  {name:<{w}}  {b}")
    return EXIT_ALLOW


def cmd_doctor(_args) -> int:
    print("VibeShield Orchestrator — Mühit Diaqnostikası")
    print("=" * 60)
    ok = True
    for name in ["audit_engine", "semgrep", "gitleaks", "trivy", "nuclei", "strix"]:
        path = resolve(name) if name != "audit_engine" else "repo daxili ✅"
        mark = "✅" if path else "🚫"
        if not path:
            ok = False
        print(f"  {mark} {name:<14} {path or 'QURULMAYIB'}")
    print("-" * 60)
    print(f"  {'✅' if os.environ.get('LLM_API_KEY') else '⏭️'} LLM_API_KEY      "
          f"{'təyin edilib (strix aktiv olacaq)' if os.environ.get('LLM_API_KEY') else 'yoxdur — strix SKIPPED'}")
    print(f"  {'✅' if shutil_which('docker') else '⏭️'} docker           "
          f"{'var' if shutil_which('docker') else 'yoxdur — strix SKIPPED'}")
    print(f"  {'✅'} node             {shutil_which('node') or 'yoxdur'}")
    print(f"  {'✅'} jq               {shutil_which('jq') or 'yoxdur'}")
    print("-" * 60)
    profiles = ", ".join(PROFILES.keys())
    print(f"  Profillər: {profiles}")
    print(f"  Repo root: {REPO_ROOT}")
    if not ok:
        print("\n  ⚠️  Əskis tool üçün: bash tools/install.sh")
        return EXIT_SETUP
    print("\n  ✅ Bütün əsas tool hazır — 'run' əmri ilə skan başladın")
    return EXIT_ALLOW


def shutil_which(name):
    return __import__("shutil").which(name)


def cmd_run(args) -> int:
    project = Path(args.project or ".").resolve()
    if not project.is_dir():
        print(f"[X] Proyekt kataloqu tapılmadı: {project}", file=sys.stderr)
        return EXIT_SETUP

    if args.out:
        out_dir = Path(args.out).resolve()
    else:
        # Scanner-ların öz hesabatını təkrar skan etməsin deyə çıxış PROYEKTİN XARİCİNDƏ tutulur
        out_dir = REPO_ROOT / "scan_out" / project.name

    pipeline = Pipeline(
        profile=args.profile,
        project=project,
        out_dir=out_dir,
        target=args.target,
        fail_on=[s.strip().lower() for s in args.fail_on.split(",")] if args.fail_on else None,
        timeout=args.timeout,
        verbose=args.verbose,
    )
    try:
        unified = pipeline.run()
    except ValueError as e:
        print(f"[X] Konfiqurasiya: {e}", file=sys.stderr)
        return EXIT_SETUP

    if args.summary:
        print(json.dumps(unified["gate"]["severity_counts"], indent=2, ensure_ascii=False))

    gate = unified["gate"]
    if not gate["passed"]:
        print(f"\n🚫 QAPI: BLOK — {gate['reason']}")
        return EXIT_BLOCK
    print(f"\n✅ QAPI: KEÇ — {gate['reason']}")
    return EXIT_ALLOW


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="vibeshield-orchestrator",
        description="Tam avtonom DevSecOps/QA/Pentest orkestratoru",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_run = sub.add_parser("run", help="DevSecOps pipeline run")
    p_run.add_argument("--project", default=".", help="skan ediləcək proyekt kataloqu")
    p_run.add_argument("--target", default=None, help="live hədəf URL (DAST: nuclei/strix)")
    p_run.add_argument("--profile", choices=list(PROFILES.keys()), default="full")
    p_run.add_argument("--out", default=None, help="nəticə kataloqu (default: <project>/scan_out)")
    p_run.add_argument("--fail-on", default=None, help='gate severities (default: profil)', )
    p_run.add_argument("--timeout", type=int, default=None, help="tool timeout saniyə")
    p_run.add_argument("--verbose", action="store_true")
    p_run.add_argument("--summary", action="store_true", help="sonunda severity JSON çap et")
    p_run.set_defaults(func=cmd_run)

    p_tools = sub.add_parser("tools", help="quraşdırılmış tool statusu")
    p_tools.set_defaults(func=cmd_tools)

    p_doc = sub.add_parser("doctor", help="mühit diaqnostikası")
    p_doc.set_defaults(func=cmd_doctor)

    args = parser.parse_args()
    if args.cmd == "run" and args.timeout is None:
        args.timeout = PROFILES[args.profile]["timeout"]
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
