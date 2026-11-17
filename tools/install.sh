#!/usr/bin/env bash
# VibeShield Tools Installer (Linux/macOS) — özü idarə edən.
# Ən son versiyaları GitHub-dan tapır, tools/bin altına quraşdırır.
# İstifadə: bash tools/install.sh
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BIN_DIR="$REPO_ROOT/tools/bin"
mkdir -p "$BIN_DIR"

# Venv aktivləşdirmə (varsa)
if [[ -f "$REPO_ROOT/.venv/bin/activate" ]]; then
  # shellcheck disable=SC1091
  source "$REPO_ROOT/.venv/bin/activate"
fi

ARCH="$(uname -m)"
OS="$(uname -s)"
if [[ "$OS" != "Linux" ]]; then
  echo "❗ Bu installer Linux üçündür. macOS üçün: brew install gitleaks trivy nuclei semgrep"
  exit 1
fi
case "$ARCH" in
  x86_64) GL_ARCH="x64"; TR_ARCH="64bit"; NU_ARCH="amd64" ;;
  aarch64|arm64) GL_ARCH="arm64"; TR_ARCH="ARM64"; NU_ARCH="arm64" ;;
  *) echo "❗ Dəstəklənməyən arxitektura: $ARCH"; exit 1 ;;
esac

gh_latest() { curl -sL "https://api.github.com/repos/$1/releases/latest" | jq -r '.tag_name'; }

echo "═══ Gitleaks ═══"
GL_VER="$(gh_latest gitleaks/gitleaks | sed 's/^v//')"
if [[ ! -x "$BIN_DIR/gitleaks" ]]; then
  curl -sL -o /tmp/gitleaks.tgz "https://github.com/gitleaks/gitleaks/releases/download/v${GL_VER}/gitleaks_${GL_VER}_linux_${GL_ARCH}.tar.gz"
  tar -xzf /tmp/gitleaks.tgz -C "$BIN_DIR" gitleaks && rm /tmp/gitleaks.tgz
  chmod +x "$BIN_DIR/gitleaks"
fi
"$BIN_DIR/gitleaks" version

echo "═══ Trivy ═══"
TR_VER="$(gh_latest aquasecurity/trivy | sed 's/^v//')"
if [[ ! -x "$BIN_DIR/trivy" ]]; then
  curl -sL -o /tmp/trivy.tgz "https://github.com/aquasecurity/trivy/releases/download/v${TR_VER}/trivy_${TR_VER}_Linux-${TR_ARCH}.tar.gz"
  tar -xzf /tmp/trivy.tgz -C "$BIN_DIR" trivy && rm /tmp/trivy.tgz
fi
"$BIN_DIR/trivy" --version

echo "═══ Nuclei ═══"
NU_VER="$(gh_latest projectdiscovery/nuclei | sed 's/^v//')"
if [[ ! -x "$BIN_DIR/nuclei" ]]; then
  curl -sL -o /tmp/nuclei.zip "https://github.com/projectdiscovery/nuclei/releases/download/v${NU_VER}/nuclei_${NU_VER}_linux_${NU_ARCH}.zip"
  unzip -o -q /tmp/nuclei.zip -d "$BIN_DIR" nuclei && rm /tmp/nuclei.zip
  chmod +x "$BIN_DIR/nuclei"
fi
"$BIN_DIR/nuclei" -version

echo "═══ Nuclei templates ═══"
"$BIN_DIR/nuclei" -ut -silent || true

echo "═══ Semgrep (pip) ═══"
python -m pip install --quiet --upgrade semgrep || echo "⚠️ semgrep pip xətası"
"$BIN_DIR/../.venv/bin/semgrep" --version 2>/dev/null || semgrep --version || true

echo "═══ Strix-agent (pip, AI pentest) ═══"
python -m pip install --quiet --upgrade strix-agent || echo "⚠️ strix-agent pip xətası (AI agent — LLM açar tələb edir)"
command -v strix && strix --version || true

echo "═══ Tool PATH məsləhəti ═══"
cat > "$BIN_DIR/PATH_INFO.txt" <<EOF
Bu tool-ları sistemdə istifadə üçün:
export PATH="$BIN_DIR:\$PATH"
EOF

echo ""
echo "✅ Bütün tool quraşdırıldı. Yoxlama:"
PATH="$BIN_DIR:$PATH" python -m orchestrator.cli tools 2>/dev/null || echo "(venv-də: python -m orchestrator.cli tools)"
