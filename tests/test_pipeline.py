"""QA: Pipeline — tam avtonom run (fast profil, real icra)."""

import json
import shutil
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from orchestrator.engine import Pipeline, PROFILES, wait_for_target  # noqa: E402


@pytest.fixture(scope="module")
def vuln_project(tmp_path_factory):
    """Məlum zəifliyi olan mini proyekt."""
    d = tmp_path_factory.mktemp("vuln_app")
    (d / "app.js").write_text(
        "const API_KEY = 'sk_test_aaaaaaaaaaa123456';\n"
        "app.get('/api/debug/env', (req,res)=>res.json({secret: API_KEY}));\n"
        "const hash = md5(input);\n"
    )
    return d


def test_profiles_exist():
    assert {"full", "fast", "qa", "pentest"} == set(PROFILES.keys())


def test_full_profile_requires_target():
    p = Pipeline(profile="full", project=Path("."), out_dir=Path("/tmp/unused"))
    with pytest.raises(ValueError):
        # nuclei/strix hədəf tələb edir, target None → xəta
        Pipeline(profile="full", project=Path("."), out_dir=Path("/tmp/unused")).run()


def test_pipeline_fast_real_run(vuln_project):
    out_dir = vuln_project / "scan_out"
    p = Pipeline(profile="fast", project=vuln_project, out_dir=out_dir)
    result = p.run()

    assert result["schema_version"] == "2.0"
    assert result["gate"]["deterministic"] is True
    # audit_engine real işləməli və API key-i tapmalı
    tools = {t["name"]: t for t in result["tools"]}
    assert tools["audit_engine"]["status"] == "OK"
    assert any(f["rule_id"] == "VS-001" for f in result["findings"])

    # unified_findings.json real fayl kimi yazılmalı
    uf = out_dir / "unified_findings.json"
    assert uf.is_file()
    data = json.loads(uf.read_text())
    assert data["gate"]["decision"] in ("BLOCK", "ALLOW")

    # report.md yaradılmalı
    assert (out_dir / "report.md").is_file()


def test_pipeline_gate_blocks_vuln_project(vuln_project):
    """Zəif proyekt → BLOCK. Deterministik."
    """
    out_dir = vuln_project / "scan_out2"
    p = Pipeline(profile="fast", project=vuln_project, out_dir=out_dir)
    result = p.run()
    # API key critical → gate BLOCK
    assert result["gate"]["decision"] == "BLOCK"
    assert result["gate"]["blocking_count"] >= 1


def test_pipeline_clean_project_allows(tmp_path):
    d = tmp_path / "clean_app"
    d.mkdir()
    (d / "main.js").write_text("const x = 1;\n")
    p = Pipeline(profile="fast", project=d, out_dir=d / "scan_out")
    result = p.run()
    assert result["gate"]["decision"] == "ALLOW"
