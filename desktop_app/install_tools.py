"""
VibeShield Tools Installer
Installs all security tools from pipeline
"""

import os
import sys
import subprocess
import urllib.request
import zipfile
import platform
from pathlib import Path

class ToolsInstaller:
    def __init__(self):
        self.is_windows = platform.system() == 'Windows'
        self.tools_dir = Path.home() / '.vibeshield' / 'tools'
        self.tools_dir.mkdir(parents=True, exist_ok=True)
        
    def log(self, message, level="INFO"):
        colors = {
            "INFO": "\033[36m",
            "SUCCESS": "\033[32m",
            "WARNING": "\033[33m",
            "ERROR": "\033[31m"
        }
        reset = "\033[0m"
        print(f"{colors.get(level, '')}{level}: {message}{reset}")
    
    def run_command(self, command, shell=True):
        """Run command and return success status"""
        try:
            result = subprocess.run(
                command,
                shell=shell,
                capture_output=True,
                text=True,
                timeout=300
            )
            return result.returncode == 0
        except Exception as e:
            self.log(f"Error running command: {e}", "ERROR")
            return False
    
    def install_python_packages(self):
        """Install Python-based tools"""
        self.log("\n=== Installing Python Packages ===", "INFO")
        
        packages = [
            'semgrep',
            'kavach-ai',
            'devsecops-radar'
        ]
        
        for package in packages:
            self.log(f"Installing {package}...", "INFO")
            if self.run_command(f"{sys.executable} -m pip install {package}"):
                self.log(f"{package} installed successfully", "SUCCESS")
            else:
                self.log(f"Failed to install {package}", "ERROR")
    
    def install_gitleaks(self):
        """Install Gitleaks"""
        self.log("\n=== Installing Gitleaks ===", "INFO")
        
        if not self.is_windows:
            self.log("Non-Windows system detected, please install manually", "WARNING")
            return
        
        version = "8.18.1"
        url = f"https://github.com/gitleaks/gitleaks/releases/download/v{version}/gitleaks_{version}_windows_x64.zip"
        zip_path = self.tools_dir / "gitleaks.zip"
        exe_path = self.tools_dir / "gitleaks.exe"
        
        try:
            self.log(f"Downloading from {url}...", "INFO")
            urllib.request.urlretrieve(url, zip_path)
            
            self.log("Extracting...", "INFO")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.tools_dir)
            
            zip_path.unlink()
            
            if exe_path.exists():
                self.log(f"Gitleaks installed to {exe_path}", "SUCCESS")
                self.add_to_path(self.tools_dir)
            else:
                self.log("Gitleaks executable not found after extraction", "ERROR")
        except Exception as e:
            self.log(f"Failed to install Gitleaks: {e}", "ERROR")
    
    def install_trivy(self):
        """Install Trivy"""
        self.log("\n=== Installing Trivy ===", "INFO")
        
        if not self.is_windows:
            self.log("Non-Windows system detected, please install manually", "WARNING")
            return
        
        version = "0.48.3"
        url = f"https://github.com/aquasecurity/trivy/releases/download/v{version}/trivy_{version}_Windows-64bit.zip"
        zip_path = self.tools_dir / "trivy.zip"
        exe_path = self.tools_dir / "trivy.exe"
        
        try:
            self.log(f"Downloading from {url}...", "INFO")
            urllib.request.urlretrieve(url, zip_path)
            
            self.log("Extracting...", "INFO")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.tools_dir)
            
            zip_path.unlink()
            
            if exe_path.exists():
                self.log(f"Trivy installed to {exe_path}", "SUCCESS")
                self.add_to_path(self.tools_dir)
            else:
                self.log("Trivy executable not found after extraction", "ERROR")
        except Exception as e:
            self.log(f"Failed to install Trivy: {e}", "ERROR")
    
    def install_nuclei(self):
        """Install Nuclei"""
        self.log("\n=== Installing Nuclei ===", "INFO")
        
        if not self.is_windows:
            self.log("Non-Windows system detected, please install manually", "WARNING")
            return
        
        version = "3.1.5"
        url = f"https://github.com/projectdiscovery/nuclei/releases/download/v{version}/nuclei_{version}_windows_amd64.zip"
        zip_path = self.tools_dir / "nuclei.zip"
        exe_path = self.tools_dir / "nuclei.exe"
        
        try:
            self.log(f"Downloading from {url}...", "INFO")
            urllib.request.urlretrieve(url, zip_path)
            
            self.log("Extracting...", "INFO")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.tools_dir)
            
            zip_path.unlink()
            
            if exe_path.exists():
                self.log(f"Nuclei installed to {exe_path}", "SUCCESS")
                self.add_to_path(self.tools_dir)
            else:
                self.log("Nuclei executable not found after extraction", "ERROR")
        except Exception as e:
            self.log(f"Failed to install Nuclei: {e}", "ERROR")
    
    def add_to_path(self, directory):
        """Add directory to PATH"""
        path_file = self.tools_dir / "path_info.txt"
        
        with open(path_file, 'w') as f:
            f.write(f"Tools installed to: {directory}\n")
            f.write(f"\nTo use these tools, add to your PATH:\n")
            f.write(f"{directory}\n")
            f.write(f"\nOr use full path:\n")
            f.write(f"{directory}\\gitleaks.exe\n")
            f.write(f"{directory}\\trivy.exe\n")
            f.write(f"{directory}\\nuclei.exe\n")
        
        self.log(f"PATH info saved to {path_file}", "INFO")
    
    def install_all(self):
        """Install all tools"""
        self.log("╔════════════════════════════════════════╗", "INFO")
        self.log("║  VibeShield Tools Installer           ║", "INFO")
        self.log("╚════════════════════════════════════════╝", "INFO")
        
        self.log(f"\nTools will be installed to: {self.tools_dir}", "INFO")
        
        # Python packages
        self.install_python_packages()
        
        # Binary tools
        if self.is_windows:
            self.install_gitleaks()
            self.install_trivy()
            self.install_nuclei()
        else:
            self.log("\n=== Manual Installation Required ===", "WARNING")
            self.log("Windows binary auto-install only supported", "WARNING")
            self.log("Please install manually:", "INFO")
            self.log("- Gitleaks: https://github.com/gitleaks/gitleaks", "INFO")
            self.log("- Trivy: https://aquasecurity.github.io/trivy/", "INFO")
            self.log("- Nuclei: https://github.com/projectdiscovery/nuclei", "INFO")
        
        self.log("\n╔════════════════════════════════════════╗", "SUCCESS")
        self.log("║  Installation Complete!                ║", "SUCCESS")
        self.log("╚════════════════════════════════════════╝", "SUCCESS")
        
        self.log(f"\nTools directory: {self.tools_dir}", "INFO")
        self.log("\nNext steps:", "INFO")
        self.log("1. Add tools directory to PATH (see path_info.txt)", "INFO")
        self.log("2. Restart terminal/IDE", "INFO")
        self.log("3. Run: START_ENTERPRISE.bat", "INFO")
        self.log("4. Test tools in UI", "INFO")


def main():
    installer = ToolsInstaller()
    
    print("\n⚠️  WARNING: This will download and install security tools")
    print(f"Installation directory: {installer.tools_dir}")
    print("\nTools to be installed:")
    print("  - Semgrep (Python)")
    print("  - Gitleaks (Binary)")
    print("  - Trivy (Binary)")
    print("  - Nuclei (Binary)")
    print("  - Kavach-AI (Python)")
    print("  - DevSecOps-Radar (Python)")
    
    response = input("\nProceed? (yes/no): ").strip().lower()
    
    if response in ['yes', 'y']:
        installer.install_all()
    else:
        print("Installation cancelled")


if __name__ == "__main__":
    main()
