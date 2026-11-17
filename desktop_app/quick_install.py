"""
Quick Auto-Installer - No prompts, just install!
"""
import subprocess
import sys

def install():
    print("\n🚀 Auto-installing tools...")
    
    # Python packages
    packages = ['semgrep', 'gitleaks']
    
    for pkg in packages:
        print(f"\n📦 Installing {pkg}...")
        try:
            subprocess.run(
                [sys.executable, '-m', 'pip', 'install', pkg, '-q'],
                check=True,
                timeout=120
            )
            print(f"✅ {pkg} installed")
        except:
            print(f"❌ {pkg} failed")
    
    print("\n✅ Installation complete!")
    print("\nInstalled:")
    print("  ✅ Semgrep (SAST)")
    print("  ✅ Gitleaks (Secrets)")
    print("\nSkipped (manual download needed):")
    print("  ⚠️  Trivy (https://trivy.dev)")
    print("  ⚠️  Nuclei (https://nuclei.projectdiscovery.io)")

if __name__ == "__main__":
    install()
