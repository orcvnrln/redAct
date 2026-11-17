"""QA: Deterministic Gate."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from orchestrator.gate import DeterministicGate  # noqa: E402


def test_block_on_critical():
    gate = DeterministicGate(["critical", "high"])
    d = gate.decision([
        {"severity": "critical", "title": "x"},
        {"severity": "medium", "title": "y"},
    ])
    assert not d["passed"] and d["decision"] == "BLOCK"
    assert d["blocking_count"] == 1


def test_block_on_high():
    gate = DeterministicGate(["critical", "high"])
    d = gate.decision([{"severity": "high", "title": "x"}])
    assert not d["passed"]


def test_allow_low_medium_info():
    gate = DeterministicGate(["critical", "high"])
    d = gate.decision([
        {"severity": "medium", "title": "a"},
        {"severity": "low", "title": "b"},
        {"severity": "info", "title": "c"},
    ])
    assert d["passed"] and d["decision"] == "ALLOW"


def test_empty_findings_allow():
    gate = DeterministicGate()
    d = gate.decision([])
    assert d["passed"] and d["severity_counts"] == {}


def test_custom_fail_on():
    gate = DeterministicGate(["critical"])
    d = gate.decision([{"severity": "high", "title": "x"}])
    assert d["passed"]


def test_deterministic_flag():
    d = DeterministicGate().decision([{"severity": "info"}])
    assert d["deterministic"] is True and d["llm_involved"] is False
