#!/usr/bin/env bash
# VibeShield Desktop başlat — Linux/macOS
#   ./start_desktop.sh              → GUI
#   ./start_desktop.sh --selftest   → headless REAL testlər
set -e
cd "$(dirname "$0")/.."

if [ -x ".venv/bin/python" ]; then
  PY=".venv/bin/python"
else
  PY="python3"
fi

export PATH="$PWD/tools/bin:$PATH"
exec "$PY" desktop_app/vibeshield_desktop.py "$@"
