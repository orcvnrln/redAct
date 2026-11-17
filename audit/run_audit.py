#!/usr/bin/env python3
"""
Audit Motor — CLI İnterfeyi
İstifadə: python -m audit.run_audit --project . --out audit_out/
"""

import json
import argparse
from pathlib import Path
from .rules import AuditEngine


def main():
    parser = argparse.ArgumentParser(description='VibeShield Audit Engine')
    parser.add_argument('--project', type=str, default='.', help='Proyekt kataloqu')
    parser.add_argument('--out', type=str, default='audit_out', help='Nəticə kataloqu')
    parser.add_argument('--fail-on', type=str, default='critical,high', 
                        help='Hansı severity-də exit 1 qaytarsın (comma-separated)')
    parser.add_argument('--extensions', type=str, default='.js,.ts,.py,.java,.go,.php,.rb',
                        help='Skan ediləcək fayl uzantıları (comma-separated)')
    
    args = parser.parse_args()
    
    project_path = Path(args.project).resolve()
    out_path = Path(args.out)
    out_path.mkdir(parents=True, exist_ok=True)
    
    extensions = [ext.strip() for ext in args.extensions.split(',')]
    fail_on = [s.strip().lower() for s in args.fail_on.split(',')]
    
    print(f"[Audit] Proyekt: {project_path}")
    print(f"[Audit] Uzantılar: {extensions}")
    print(f"[Audit] Fail-on: {fail_on}")
    
    # Skan başlat
    engine = AuditEngine()
    findings = engine.scan_project(project_path, extensions)
    summary = engine.get_summary(findings)
    
    # JSON olaraq saxla
    output = {
        "findings": findings,
        "summary": summary,
        "deterministic": True,
        "llm_involved": False,
    }
    
    findings_file = out_path / "audit_findings.json"
    with open(findings_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    # Konsola çap et
    print(f"\n{'='*50}")
    print(f"[Audit] Nəticələr:")
    print(f"  Ümumi:   {summary['total']}")
    print(f"  Kritik:  {summary['critical']}")
    print(f"  Yüksək:  {summary['high']}")
    print(f"  Orta:    {summary['medium']}")
    print(f"  Aşağı:   {summary['low']}")
    print(f"{'='*50}\n")
    
    print(f"[Audit] Nəticələr saxlanıldı: {findings_file}")
    
    # Deterministik qapı qərarı
    critical_count = sum(
        1 for f in findings if f['severity'] in fail_on
    )
    
    if critical_count > 0:
        print(f"\n🚫 QAPI BLOKLANDI: {critical_count} {fail_on} severity tapıntı")
        exit(1)
    else:
        print(f"\n✅ QAPI KEÇDƏ: {fail_on} severity tapıntı yoxdur")
        exit(0)


if __name__ == '__main__':
    main()
