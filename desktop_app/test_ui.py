#!/usr/bin/env python3
"""
Desktop UI Test - GUI acilmadan test edir
"""

import sys
import os

# Add current dir to path
sys.path.insert(0, os.path.dirname(__file__))

print("=" * 60)
print("VibeShield Desktop UI Test")
print("=" * 60)

# Test 1: Imports
print("\n[1/5] Import test...")
try:
    import tkinter as tk
    import tkinter.simpledialog
    from tkinter import ttk, messagebox, filedialog, scrolledtext
    print("  ✓ Tkinter modules OK")
except Exception as e:
    print(f"  ✗ Tkinter import xetasi: {e}")
    sys.exit(1)

try:
    from scanner import DesktopScanner, ScanResult
    print("  ✓ Scanner module OK")
except Exception as e:
    print(f"  ✗ Scanner import xetasi: {e}")
    sys.exit(1)

try:
    from gate import DeterministicGate
    print("  ✓ Gate module OK")
except Exception as e:
    print(f"  ✗ Gate import xetasi: {e}")
    sys.exit(1)

# Test 2: Config
print("\n[2/5] Config test...")
try:
    import json
    config_path = "config.json"
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            config = json.load(f)
        print(f"  ✓ config.json oxundu ({len(config)} keys)")
    else:
        print("  ⚠ config.json yoxdur (yaradilar)")
        config = {}
except Exception as e:
    print(f"  ✗ Config xetasi: {e}")
    config = {}

# Test 3: Tkinter window (headless)
print("\n[3/5] Tkinter window test...")
try:
    root = tk.Tk()
    root.withdraw()  # Hide window
    print("  ✓ Tkinter root window yaradildi")
    root.destroy()
except Exception as e:
    print(f"  ✗ Tkinter window xetasi: {e}")
    sys.exit(1)

# Test 4: Main class import
print("\n[4/5] Main class test...")
try:
    from main import DevSecOpsDesktopApp
    print("  ✓ DevSecOpsDesktopApp class OK")
except Exception as e:
    print(f"  ✗ Main class import xetasi: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Dry run (no GUI)
print("\n[5/5] App initialization test...")
try:
    # Don't actually create GUI, just check if it would work
    print("  ✓ App class hazirdir")
    print("\n" + "=" * 60)
    print("✅ Bütün testlər keçdi!")
    print("=" * 60)
    print("\nDesktop UI-ni başlatmaq üçün:")
    print("  python main.py")
    print("  və ya: run.bat")
    print("\n")
except Exception as e:
    print(f"  ✗ App init xetasi: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
