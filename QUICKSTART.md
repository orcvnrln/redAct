# VibeShield — 5 Dəqiqəlik Başlanğıc

Bu təlimat sistemin 5 dəqiqədə lokal və ya GitHub Actions-da işə salınması üçündür.

## Ön Şərtlər

**Hazırda sisteminizdə:**
- ✅ Python 3.12.10
- ✅ Node.js 26.13.0
- ✅ Audit Engine (13 qayda)
- ✅ Desktop UI

**Quraşdırılmalı:**
- ❌ Git ([yükləyin](https://git-scm.com/downloads))
- ❌ Docker Desktop ([yükləyin](https://www.docker.com/products/docker-desktop))
- ❌ jq (`choco install jq` və ya [manual](https://stedolan.github.io/jq/download/))
- ❌ Gitleaks (`choco install gitleaks`)
- ❌ Semgrep (`pip install semgrep`)
- ❌ Trivy (`choco install trivy`)

**Yoxlama:**
```bash
python scripts/check_system.py
# və ya manuel: git --version, docker --version, jq --version
```

## Lokal Test (3 dəqiqə)

### 1. Asılılıqları Quraşdırın

```bash
# Python paketi
pip install -e .

# Target app
cd target_app
npm install
cd ..
```

### 2. Audit Motorunu Test Edin

```bash
# Target app-da qəsdən zəifliklər var, audit tutmalıdır
python -m audit.run_audit --project target_app --out audit_out/

# Gözlənilən nəticə: Exit 1 (zəiflik tapıldı)
# audit_out/audit_findings.json yaradılmalıdır
```

### 3. Desktop UI-ni Başladın (İstəyə görə)

```bash
cd desktop_app
python main.py
```

Açılacaq panel:
- **Scan** düyməsi — Lokal proyekti skan edir
- **Gate** düyməsi — unified_findings.json-dan qərar simulyasiyası

### 4. Sandbox Test (Docker lazımdır)

```bash
# Sandbox-ı başlat
docker compose -f docker-compose.sandbox.yml up -d

# Hədəfin hazır olduğunu yoxla
curl http://localhost:8000/health
# Gözlənilən: {"status":"ok"}

# Zəifliyi əl ilə test et (IDOR)
curl http://localhost:8000/api/profile/1
curl http://localhost:8000/api/profile/2
# Hər iki sorğu işləməli (auth yoxdur — zəiflik)

# Sandbox-ı söndür
docker compose -f docker-compose.sandbox.yml down
```

## GitHub Actions Test (2 dəqiqə)

### 1. GitHub-a Yükləyin

```bash
git init
git add .
git commit -m "feat: initial VibeShield setup"
git branch -M main
git remote add origin https://github.com/<username>/<repo>.git
git push -u origin main
```

### 2. Secrets Konfiqurasiyası

GitHub-da:
1. Repository → **Settings**
2. **Secrets and variables** → **Actions**
3. **New repository secret**:
   - **Name:** `OPENROUTER_API_KEY`
   - **Value:** `sk-or-v1-...` (OpenRouter-dan alın)

### 3. Pipeline-ı İzləyin

1. GitHub-da **Actions** tab-ına keçin
2. "7-Addimli Deterministik DevSecOps" workflow-u görməlisiniz
3. Son commit üçün run başlayacaq

### Gözlənilən Nəticə

Pipeline **uğursuz** olmalıdır çünki `target_app`-da qəsdən zəifliklər var:

```
✅ Addım 1: Build + Test (keçir)
✅ Addım 2: Statik Skan (continue-on-error, keçir)
❌ Addım 2.5: Audit Engine (4 zəiflik tapır, exit 1)
```

Audit zəiflik tapdığı üçün sonrakı addımlar (Sandbox, Strix) işləməyəcək — bu gözləniləndədir!

## Zəiflikləri Düzəldin (Audit keçməsi üçün)

`target_app/server.js`-də aşağıdakı dəyişikliklər edin:

### 1. Secret-i Silin

```javascript
// ❌ Əvvəl
const API_SECRET = 'sk_test_abc123def456ghi789';

// ✅ Sonra (environment variable)
const API_SECRET = process.env.API_SECRET || 'fallback';
```

### 2. Debug Endpoint-i Silin

```javascript
// ❌ Bu endpoint-i silin
app.get('/api/debug/env', (req, res) => {
  res.json({ secret: API_SECRET });
});
```

### 3. Auth Middleware Əlavə Edin

```javascript
// Auth middleware
const authMiddleware = (req, res, next) => {
  const token = req.headers['authorization'];
  if (!token) {
    return res.status(401).json({ error: 'Unauthorized' });
  }
  // Token validation (sadə nümunə)
  if (token !== 'Bearer valid-token') {
    return res.status(403).json({ error: 'Forbidden' });
  }
  next();
};

// Route-lara əlavə edin
app.get('/api/users/:id', authMiddleware, (req, res) => {
  // ...
});

app.get('/api/profile/:id', authMiddleware, (req, res) => {
  // Ownership yoxlaması
  const requestedId = parseInt(req.params.id);
  const tokenUserId = 1; // Token-dan alınmalıdır
  
  if (requestedId !== tokenUserId) {
    return res.status(403).json({ error: 'Access denied' });
  }
  // ...
});
```

### 4. Yenidən Push Edin

```bash
git add target_app/server.js
git commit -m "fix: security issues in target_app"
git push origin main
```

İndi pipeline **keçməlidir**:

```
✅ Addım 1: Build + Test
✅ Addım 2: Statik Skan
✅ Addım 2.5: Audit Engine (zəiflik yoxdur)
✅ Addım 3: Sandbox Deploy
✅ Addım 4: Strix (LLM key varsa, yoxsa Nuclei)
✅ Addım 6: Qapı (critical/high = 0)
✅ Addım 7: Hesabat
✅ Publish (echo mesajı)
```

## Strix Test (LLM lazımdır)

Əgər OpenRouter API key-iniz varsa:

```bash
# Environment təyin edin
export LLM_API_KEY="sk-or-v1-..."
export STRIX_LLM="openrouter/google/gemma-2-9b-it"

# Sandbox-ı başladın
docker compose -f docker-compose.sandbox.yml up -d

# Strix-i işlədin (zəiflikli target_app üçün)
./pentest/run-scan.sh

# Gözlənilən: findings.json yaradılır, exit 2
```

## Təmizlik

```bash
# Docker-i təmizlə
docker compose -f docker-compose.sandbox.yml down -v

# Test faylları
rm -rf audit_out/ findings.json nuclei.json test_*
```

## Növbəti Addımlar

### 1. Desktop App-i İnkişaf Etdirin

```bash
cd desktop_app
python main.py
```

- Lokal projektləri skan edin
- Nəticələri real-time görün
- Gate simulyasiyası edin

### 2. Audit Qayda Əlavə Edin

`audit/rules.py`-də yeni qayda əlavə edin:

```python
AuditRule(
    rule_id="VS-014",
    name="JWT Secret Weakness",
    severity="high",
    pattern=r'jwt\.sign\([^)]*[\'"][a-zA-Z0-9]{1,10}[\'"]',
    description="JWT secret çox qısadır - ən azı 32 simvol olmalıdır",
    cwe="CWE-326",
    owasp="A02:2021"
)
```

### 3. CI/CD-yə Əlavə Addımlar

`.github/workflows/devsecops.yml`-də `publish` job-unu real deploy ilə əvəz edin:

```yaml
publish:
  needs: gate
  runs-on: ubuntu-latest
  steps:
    - name: Docker Build & Push
      run: |
        docker build -t myapp:${{ github.sha }} .
        docker push myapp:${{ github.sha }}
    
    - name: Deploy to K8s
      run: |
        kubectl set image deployment/myapp \
          myapp=myapp:${{ github.sha }}
```

## Çox Soruşulan Suallar

### Q: Pipeline çox yavaşdır (15 dəqiqə)

**A:** Strix-i deaktiv edin və ya `scan-mode: quick` istifadə edin. Yalnız statik qat istəyirsinizsə, Addım 4-ü şərti edin:

```yaml
- name: Strix Attack
  if: github.event_name == 'pull_request'  # Yalnız PR-da
  run: ./pentest/run-scan.sh
```

### Q: OpenRouter API key-im yoxdur

**A:** Strix Addımı fallback-ə keçir və Nuclei işlədər. Və ya yalnız statik qatı işlədin (Audit Engine kifayətdir).

### Q: Audit Engine false positive verir

**A:** `audit/rules.py`-də regex pattern-i düzəldin. Məsələn, test fayllarını atlayın:

```python
def scan_project(self, project_path, extensions):
    for file_path in project_path.rglob('*'):
        # Test fayllarını atla
        if 'test' in file_path.stem.lower():
            continue
        # ...
```

### Q: Desktop app açılmır

**A:** Asılılıqları yoxlayın:

```bash
pip install customtkinter Pillow
cd desktop_app
python main.py
```

### Q: Docker sandbox işləmir

**A:** Docker daemon-un işlədiyindən əmin olun:

```bash
docker --version
docker ps
```

## Əlaqə və Dəstək

- **GitHub Issues:** Təkliflər və xətalar üçün
- **Discussions:** Suallar və müzakirələr üçün
- **Architecture:** `ARCHITECTURE.md`-yə baxın

---

**Tövsiyə:** İlk dəfə `target_app`-ı zəiflikli saxlayıb pipeline-ın bloklamasını görün, sonra düzəldib keçməsini müşahidə edin. Bu, sistemin necə işlədiyini başa düşməyin ən yaxşı yoludur.
