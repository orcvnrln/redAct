#!/usr/bin/env bash
# Sistemin tam test skripti
# İstifadə: ./test_system.sh

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo -e "${BLUE}  VibeShield System Test${NC}"
echo -e "${BLUE}═══════════════════════════════════════${NC}\n"

# Test 1: Audit Engine
echo -e "${YELLOW}[1/5] Audit Engine Test...${NC}"
if python -m audit.run_audit --project target_app --out test_audit_out/ --fail-on critical,high 2>/dev/null; then
    echo -e "${RED}  ✗ Audit keçdi (zəiflik olmalıdır!)${NC}"
    exit 1
else
    EXIT_CODE=$?
    if [ $EXIT_CODE -eq 1 ]; then
        echo -e "${GREEN}  ✓ Audit düzgün zəiflik tapdı${NC}"
    else
        echo -e "${RED}  ✗ Gözlənilməz xəta: exit $EXIT_CODE${NC}"
        exit 1
    fi
fi

# Test 2: Gate Module
echo -e "\n${YELLOW}[2/5] Gate Module Test...${NC}"
python -c "
from desktop_app.gate import DeterministicGate
import json

# Fake findings yarat
test_data = {
    'findings': [
        {'severity': 'critical', 'title': 'Test 1'},
        {'severity': 'high', 'title': 'Test 2'},
        {'severity': 'medium', 'title': 'Test 3'},
    ]
}
with open('test_findings.json', 'w') as f:
    json.dump(test_data, f)

gate = DeterministicGate()
passed, critical_count, severity_counts = gate.evaluate('test_findings.json')

assert not passed, 'Gate keçməməli (2 critical/high var)'
assert critical_count == 2, f'Critical count səhvdir: {critical_count}'
assert severity_counts['critical'] == 1, 'Critical count səhvdir'
assert severity_counts['high'] == 1, 'High count səhvdir'

print('✓ Gate düzgün işləyir')
" && echo -e "${GREEN}  ✓ Gate test keçdi${NC}" || { echo -e "${RED}  ✗ Gate test uğursuz${NC}"; exit 1; }

# Test 3: Docker Compose Syntax
echo -e "\n${YELLOW}[3/5] Docker Compose Syntax...${NC}"
if docker compose -f docker-compose.sandbox.yml config >/dev/null 2>&1; then
    echo -e "${GREEN}  ✓ Docker Compose konfiqurasiyası düzgündür${NC}"
else
    echo -e "${RED}  ✗ Docker Compose konfiqurasiyası səhvdir${NC}"
    exit 1
fi

# Test 4: Target App Dependencies
echo -e "\n${YELLOW}[4/5] Target App Dependencies...${NC}"
if [ -f target_app/package.json ]; then
    cd target_app
    if npm install --silent 2>/dev/null; then
        echo -e "${GREEN}  ✓ Target app dependencies quruldu${NC}"
    else
        echo -e "${RED}  ✗ npm install uğursuz${NC}"
        exit 1
    fi
    cd ..
else
    echo -e "${RED}  ✗ target_app/package.json tapılmadı${NC}"
    exit 1
fi

# Test 5: Pentest Script Syntax
echo -e "\n${YELLOW}[5/5] Pentest Script Syntax...${NC}"
if bash -n pentest/run-scan.sh 2>/dev/null; then
    echo -e "${GREEN}  ✓ run-scan.sh sintaksisi düzgündür${NC}"
else
    echo -e "${RED}  ✗ run-scan.sh sintaksis xətası${NC}"
    exit 1
fi

# Təmizlik
rm -f test_findings.json
rm -rf test_audit_out/

echo -e "\n${BLUE}═══════════════════════════════════════${NC}"
echo -e "${GREEN}  ✅ Bütün testlər keçdi!${NC}"
echo -e "${BLUE}═══════════════════════════════════════${NC}\n"

echo -e "${YELLOW}Növbəti addımlar:${NC}"
echo -e "  1. GitHub Secrets konfiqurasiyası (OPENROUTER_API_KEY)"
echo -e "  2. git push origin main"
echo -e "  3. GitHub Actions-da pipeline-ı izləyin"
echo -e ""
