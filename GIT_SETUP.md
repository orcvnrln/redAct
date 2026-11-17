# Git Setup Guide for VibeShield

## ⚠️ Git Not Installed

Git is not currently installed on your system. Follow these steps:

## 🔧 Install Git

### Option 1: Official Git for Windows
```
1. Download: https://git-scm.com/download/win
2. Run installer (use default settings)
3. Restart terminal/IDE
```

### Option 2: GitHub Desktop (Easier)
```
1. Download: https://desktop.github.com/
2. Install and sign in
3. Use GUI to manage repo
```

## 📝 After Git is Installed

Run these commands in your project folder:

```bash
# Initialize repo
git init

# Add all files
git add .

# First commit
git commit -m "Initial commit: VibeShield Security Suite"

# Set main branch
git branch -M main

# Add remote
git remote add origin https://github.com/orcvnrln/redAct.git

# Push to GitHub
git push -u origin main
```

## 🔐 GitHub Authentication

### Personal Access Token (Recommended)
```
1. Go to: https://github.com/settings/tokens
2. Generate new token (classic)
3. Select scopes: repo, workflow
4. Copy token
5. Use as password when pushing
```

### Or SSH Key
```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"

# Add to GitHub
# Settings > SSH and GPG keys > New SSH key
```

## 📂 Files to Commit

Already created:
- ✅ README.md
- ✅ .github/workflows/devsecops.yml
- ✅ desktop_app/vibeshield_ontology.py
- ✅ audit/ folder with rules
- ✅ All configuration files

## 🚀 Quick Script

After installing Git, run this:

```bash
cd c:\Users\Spark\Desktop\ssimi

git init
git add .
git commit -m "Initial commit: VibeShield Security Suite with Ontology UI"
git branch -M main
git remote add origin https://github.com/orcvnrln/redAct.git
git push -u origin main
```

## 📋 .gitignore

Create `.gitignore` to exclude sensitive files:

```
# Config with secrets
desktop_app/config.json

# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so

# Virtual env
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Build
dist/
build/
*.egg-info/

# Logs
*.log

# Output
audit_out/
*.json.bak
report.pdf

# Tools
.vibeshield/
```

## ✅ Checklist

- [ ] Install Git
- [ ] Restart terminal
- [ ] Create .gitignore
- [ ] Run git init
- [ ] Commit all files
- [ ] Push to GitHub
- [ ] Verify on github.com

## 🎯 Next Steps

After pushing to GitHub:
1. Go to: https://github.com/orcvnrln/redAct
2. Add description and topics
3. Enable GitHub Actions
4. Add secrets (OPENROUTER_API_KEY)
5. Test pipeline on next push

---

**Need help?** Check: https://docs.github.com/en/get-started
