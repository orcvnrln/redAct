# redAct - VibeShield Security Suite

🛡️ **Enterprise-grade DevSecOps platform with AI-powered security scanning**

## 🎯 Features

- **Multi-Tool Security Scanning**: Audit Engine, Semgrep, Gitleaks, Nuclei, Trivy, Strix AI
- **Professional Desktop UI**: Ontology-inspired minimalist design with sidebar navigation
- **GitHub Actions Pipeline**: 7-step deterministic DevSecOps workflow
- **AI-Powered Pentesting**: Strix AI with OpenRouter integration
- **Real-Time Monitoring**: Live scan output with terminal-style logging
- **API Key Management**: GitHub Token + OpenRouter API configuration

## 🚀 Quick Start

### Tam Avtonom Orkestrator (CLI) — tövsiyə olunur

```bash
source .venv/bin/activate
export PATH="$PWD/tools/bin:$PATH"

# Mühit diaqnostikası
python -m orchestrator.cli doctor

# Tam pipeline: SAST + secrets + SCA + canlı DAST
node target_app/server.js &
python -m orchestrator.cli run --project ./target_app --target http://localhost:8000 --profile full

# Profillər: full | fast | qa | pentest   (çıxış kodu: 0=keç, 1=blok)
```

Ətraflı: [ORCHESTRATOR.md](ORCHESTRATOR.md)

### Desktop Application

```bash
install_tools.ps1

# Launch UI
START_ONTOLOGY.bat
```

### GitHub Actions Pipeline

Pipeline automatically runs on push/PR:
1. Build & Unit Test
2. Static Analysis (Gitleaks, Semgrep, Trivy, Audit Engine)
3. Code Quality Gate (SonarQube)
4. Sandbox Deploy
5. AI Pentest (Strix + OpenRouter)
6. Deterministic Security Gate
7. Unified Reporting

## 📊 Tools Coverage

| Tool | Type | Status |
|------|------|--------|
| Audit Engine | SAST | ✅ Active |
| Semgrep | SAST | ✅ Active |
| Gitleaks | Secrets | ✅ Active |
| Nuclei | Templates/DAST | ✅ Active |
| Trivy | SCA+Secrets+IaC | ✅ Active |
| Strix | AI DAST | ⚙️ Şərti (Docker + LLM_API_KEY tələb edir, yoxdursa SKIPPED) |

> Windows installer (`install_tools.py`) əvəzinə Linux/macOS-da `bash tools/install.sh` istifadə edin.

## 🎨 UI Design

- **Style**: Vercel + Linear + Ontology
- **Layout**: 240px sidebar + centered content
- **Navigation**: 4 views (Scan, Monitor, Results, Settings)
- **Theme**: Ultra-minimalist dark with perfect spacing

## 🔧 Configuration

### Required Secrets (GitHub Actions)
```yaml
OPENROUTER_API_KEY: Your OpenRouter API key
GITHUB_TOKEN: Automatically provided by GitHub
SONAR_TOKEN: Optional SonarQube token
```

### Local Configuration (`config.json`)
```json
{
  "openrouter_api_key": "sk-...",
  "github_token": "ghp_...",
  "target_url": "http://localhost:8000",
  "project_path": "C:\\path\\to\\project"
}
```

## 📁 Project Structure

```
├── .github/workflows/
│   └── devsecops.yml          # 7-step pipeline
├── desktop_app/
│   ├── vibeshield_ontology.py # Main UI
│   ├── config.json            # User settings
│   └── install_tools.py       # Tool installer
├── audit/
│   ├── rules.py               # 13 security rules
│   └── run_audit.py           # Audit engine
├── pentest/
│   ├── run-scan.sh            # Strix runner
│   └── nuclei-scan.sh         # Nuclei fallback
└── target_app/
    └── server.js              # Sample vulnerable app

```

## 🧪 Running Scans

### Desktop UI
1. Launch: `START_ONTOLOGY.bat`
2. Select project path
3. Click "▶ Full Scan"
4. Monitor live output

### Command Line
```bash
# Audit only
python -m audit.run_audit --project ./myapp

# With Semgrep
semgrep --config=auto ./myapp

# With Gitleaks
gitleaks detect --source ./myapp
```

## 📊 Pipeline Results

Pipeline generates:
- `unified_findings.json` - All tool results
- `report.pdf` - Comprehensive security report
- Artifact uploads for CI/CD integration

## 🎯 Security Gate

Deterministic gate blocks deployment if:
- Critical/High severity findings exist
- Uses jq-based JSON parsing (no LLM involvement)
- Exit code 1 = blocked, 0 = passed

## 🤖 AI Features

- **Strix AI Pentest**: LLM-powered vulnerability discovery
- **Kavach Auto-Fix**: Automatic PR creation for fixes
- **AI Security Assistant**: Built-in chat for security questions

## 🛠️ Installation

### Windows
```powershell
# Install all tools
powershell -ExecutionPolicy Bypass -File install_tools.ps1

# Or install individually
pip install semgrep
# Download gitleaks, trivy, nuclei from GitHub releases
```

### Linux/Mac
```bash
# Install Python tools
pip install semgrep

# Install binaries
brew install gitleaks trivy nuclei
```

## 📖 Documentation

- [Tool Status](TOOLS_STATUS.md) - Current tool availability
- [Design System](docs/DESIGN.md) - UI design principles
- [Pipeline Guide](.github/workflows/README.md) - CI/CD setup

## 🔐 Security

- All secrets masked in UI
- Config stored locally in `config.json`
- No credentials in git history
- Deterministic gate (no LLM bias)

## 🎨 Screenshots

### Scan View
![Scan](docs/screenshots/scan.png)

### Monitor View
![Monitor](docs/screenshots/monitor.png)

### Settings View
![Settings](docs/screenshots/settings.png)

## 🤝 Contributing

1. Fork the repo
2. Create feature branch
3. Run full scan
4. Submit PR (pipeline auto-runs)

## 📜 License

MIT License - See [LICENSE](LICENSE)

## 🌟 Credits

- **Design**: Inspired by Vercel, Linear, Ontology
- **Tools**: Semgrep, Gitleaks, Trivy, Nuclei, Strix
- **AI**: OpenRouter API integration

## 📞 Support

- Issues: [GitHub Issues](https://github.com/orcvnrln/redAct/issues)
- Docs: [Wiki](https://github.com/orcvnrln/redAct/wiki)

---

**Built with ❤️ for DevSecOps teams**

🛡️ **VibeShield** - Security made simple and beautiful
