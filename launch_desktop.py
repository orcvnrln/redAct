#!/usr/bin/env python3
"""
VibeShield Desktop Launcher
Desktop app-i background process kimi basladir
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    print("=" * 60)
    print("  VibeShield Desktop Launcher")
    print("=" * 60)
    print()
    
    # Check desktop_app exists
    desktop_app_dir = Path(__file__).parent / "desktop_app"
    main_py = desktop_app_dir / "main.py"
    
    if not main_py.exists():
        print(f"[XETA] {main_py} tapilmadi!")
        print()
        input("Enter basin...")
        sys.exit(1)
    
    print(f"[OK] Desktop app tapildi: {main_py}")
    print()
    print("Desktop UI baslayir...")
    print("Yeni pencere acilacaq...")
    print()
    
    # Launch in new process
    try:
        if sys.platform == "win32":
            # Windows: pythonw.exe ile background-da
            pythonw = sys.executable.replace("python.exe", "pythonw.exe")
            if os.path.exists(pythonw):
                subprocess.Popen(
                    [pythonw, str(main_py)],
                    cwd=str(desktop_app_dir),
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                print("[OK] Desktop UI baslatildi (background)")
            else:
                # Fallback: normal python
                subprocess.Popen(
                    [sys.executable, str(main_py)],
                    cwd=str(desktop_app_dir)
                )
                print("[OK] Desktop UI baslatildi")
        else:
            # Linux/Mac
            subprocess.Popen(
                [sys.executable, str(main_py)],
                cwd=str(desktop_app_dir)
            )
            print("[OK] Desktop UI baslatildi")
        
        print()
        print("=" * 60)
        print("  Pencere acildi. Bu terminali baglaya bilersiniz.")
        print("=" * 60)
        print()
        
    except Exception as e:
        print(f"[XETA] Baslama xetasi: {e}")
        print()
        print("Manual baslatma:")
        print("  cd desktop_app")
        print("  python main.py")
        print()
        input("Enter basin...")
        sys.exit(1)

if __name__ == "__main__":
    main()
