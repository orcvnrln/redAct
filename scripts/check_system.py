#!/usr/bin/env python3
"""
VibeShield - Sistem Yoxlama Skripti
Bütün lazım olan alətlərin quraşdırılıb-quraşdırılmadığını yoxlayır
"""

import subprocess
import sys
import os
from pathlib import Path


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'


def check_command(cmd, name, required=True):
    """Əmrin mövcudluğunu yoxlayır"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version = result.stdout.strip().split('\n')[0]
            print(f"{Colors.GREEN}✓{Colors.END} {name}: {version}")
            return True
        else:
            if required:
                print(f"{Colors.RED}✗{Colors.END} {name}: Quraşdırılmayıb")
            else:
                print(f"{Colors.YELLOW}⚠{Colors.END} {name}: Quraşdırılmayıb (istəyə görə)")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        if required:
            print(f"{Colors.RED}✗{Colors.END} {name}: Tapılmadı")
        else:
            print(f"{Colors.YELLOW}⚠{Colors.END} {name}: Tapılmadı (istəyə görə)")
        return False


def check_python_package(package, name, required=True):
    """Python paketinin quraşdırılıb-quraşdırılmadığını yoxlayır"""
    try:
        __import__(package)
        print(f"{Colors.GREEN}✓{Colors.END} {name}: Quraşdırılıb")
        return True
    except ImportError:
        if required:
            print(f"{Colors.RED}✗{Colors.END} {name}: Quraşdırılmayıb")
        else:
            print(f"{Colors.YELLOW}⚠{Colors.END} {name}: Quraşdırılmayıb (istəyə görə)")
        return False


def check_file(path, name):
    """Faylın mövcudluğunu yoxlayır"""
    if os.path.exists(path):
        print(f"{Colors.GREEN}✓{Colors.END} {name}: Mövcuddur")
        return True
    else:
        print(f"{Colors.RED}✗{Colors.END} {name}: Tapılmadı")
        return False


def main():
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}  VibeShield Sistem Yoxlaması{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'='*60}{Colors.END}\n")

    results = {
        'required': [],
        'recommended': [],
        'optional': []
    }

    # ================================================================
    # P0: Mütləq Lazım
    # ================================================================
    print(f"{Colors.BOLD}[P0] Mütləq Tələblər:{Colors.END}\n")

    results['required'].append(check_command("python --version", "Python 3.8+", required=True))
    results['required'].append(check_command("node --version", "Node.js 18+", required=True))
    results['required'].append(check_command("git --version", "Git", required=True))
    results['required'].append(check_command("docker --version", "Docker", required=True))
    
    # jq - Windows-da path problemi ola bilər
    if sys.platform == "win32":
        results['required'].append(check_command("where jq", "jq (JSON processor)", required=True))
    else:
        results['required'].append(check_command("which jq", "jq (JSON processor)", required=True))

    # Python paketləri
    results['required'].append(check_python_package("yaml", "PyYAML", required=True))
    results['required'].append(check_python_package("requests", "requests", required=True))

    # Audit Engine
    audit_path = Path(__file__).parent.parent / "audit" / "__init__.py"
    results['required'].append(check_file(audit_path, "Audit Engine"))

    print()

    # ================================================================
    # P1: Tövsiyə Olunan (Statik Qat)
    # ================================================================
    print(f"{Colors.BOLD}[P1] Tövsiyə Olunan (Statik Skan):{Colors.END}\n")

    results['recommended'].append(check_command("gitleaks version", "Gitleaks", required=False))
    results['recommended'].append(check_command("semgrep --version", "Semgrep", required=False))
    results['recommended'].append(check_command("trivy --version", "Trivy", required=False))

    print()

    # ================================================================
    # P2: İstəyə Görə (Dinamik Qat)
    # ================================================================
    print(f"{Colors.BOLD}[P2] İstəyə Görə (Dinamik Skan + AI):{Colors.END}\n")

    results['optional'].append(check_command("strix --version", "Strix", required=False))
    results['optional'].append(check_command("nuclei -version", "Nuclei", required=False))
    results['optional'].append(check_command("sonar-scanner --version", "Sonar Scanner", required=False))

    print()

    # ================================================================
    # Konfiqurasiya Faylları
    # ================================================================
    print(f"{Colors.BOLD}[Konfiqurasiya] Fayllar:{Colors.END}\n")

    config_checks = []
    desktop_config = Path(__file__).parent.parent / "desktop_app" / "config.json"
    config_checks.append(check_file(desktop_config, "Desktop UI config.json"))

    workflow = Path(__file__).parent.parent / ".github" / "workflows" / "devsecops.yml"
    config_checks.append(check_file(workflow, "GitHub Actions workflow"))

    docker_compose = Path(__file__).parent.parent / "docker-compose.sandbox.yml"
    config_checks.append(check_file(docker_compose, "Docker Compose sandbox"))

    print()

    # ================================================================
    # Xülasə
    # ================================================================
    print(f"{Colors.CYAN}{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}Xülasə:{Colors.END}\n")

    required_count = sum(results['required'])
    required_total = len(results['required'])
    recommended_count = sum(results['recommended'])
    recommended_total = len(results['recommended'])
    optional_count = sum(results['optional'])
    optional_total = len(results['optional'])

    print(f"  Mütləq:        {required_count}/{required_total} ✓")
    print(f"  Tövsiyə:       {recommended_count}/{recommended_total} ✓")
    print(f"  İstəyə görə:   {optional_count}/{optional_total} ✓")

    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*60}{Colors.END}\n")

    # ================================================================
    # Tövsiyələr
    # ================================================================
    if required_count < required_total:
        print(f"{Colors.RED}{Colors.BOLD}⚠ XƏTA:{Colors.END} Mütləq tələblər ödənilməyib!\n")
        print(f"{Colors.YELLOW}Tövsiyələr:{Colors.END}")
        print("  1. Python, Node.js, Git, Docker quraşdırın")
        print("  2. jq quraşdırın: choco install jq (Windows)")
        print("  3. pip install -e . (Audit Engine)")
        print(f"\nDaha ətraflı: {Colors.BLUE}SETUP_CHECKLIST.md{Colors.END}\n")
        sys.exit(1)
    elif recommended_count < recommended_total:
        print(f"{Colors.YELLOW}{Colors.BOLD}⚠ XƏBƏRDARLIQ:{Colors.END} Bəzi tövsiyə olunan alətlər yoxdur.\n")
        print(f"{Colors.YELLOW}Tövsiyələr:{Colors.END}")
        if not results['recommended'][0]:  # Gitleaks
            print("  - Gitleaks: choco install gitleaks")
        if not results['recommended'][1]:  # Semgrep
            print("  - Semgrep: pip install semgrep")
        if not results['recommended'][2]:  # Trivy
            print("  - Trivy: choco install trivy")
        print(f"\nSistem işləyir, lakin tam təhlükəsizlik üçün bu alətlər lazımdır.")
        print(f"Daha ətraflı: {Colors.BLUE}SETUP_CHECKLIST.md{Colors.END}\n")
        sys.exit(0)
    else:
        print(f"{Colors.GREEN}{Colors.BOLD}✅ Əla!{Colors.END} Bütün mütləq və tövsiyə olunan komponentlər hazırdır.\n")
        
        if optional_count < optional_total:
            print(f"{Colors.YELLOW}Qeyd:{Colors.END} Strix/Nuclei dinamik skan üçün istəyə görədir.")
            print(f"      OpenRouter API key: https://openrouter.ai\n")
        
        print(f"{Colors.GREEN}Növbəti addım:{Colors.END}")
        print("  1. Desktop UI: cd desktop_app && python main.py")
        print("  2. Lokal test: python -m audit.run_audit --project target_app --out audit_out")
        print("  3. GitHub push: git push origin main\n")
        sys.exit(0)


if __name__ == "__main__":
    main()
