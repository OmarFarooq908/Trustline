"""End-to-end ACME Stream audit tests."""

from __future__ import annotations

import json
from pathlib import Path

from trustline.config import load_profile, resolve_duckdb_path
from trustline.contracts.audit_profile import load_audit_profile
from trustline.contracts.loader import load_contracts_dir
from trustline.executors.duckdb import DuckDBExecutor
from trustline.scorecard.orchestrator import run_full_audit

REPO_ROOT = Path(__file__).resolve().parents[2]
ACME_ROOT = REPO_ROOT / "examples" / "acme_stream"
ACME_CONTRACTS = ACME_ROOT / "contracts"
ACME_PROFILES = ACME_ROOT / "profiles.yml.example"
MOCK_RESULTS = REPO_ROOT / "tests" / "fixtures" / "acme_funnel_mock_results.json"


def _run_acme_audit():
    profile = load_profile("default", ACME_PROFILES)
    contracts = load_contracts_dir(ACME_CONTRACTS)
    audit_profile = load_audit_profile(ACME_ROOT / "audit_profile.yaml")
    database = resolve_duckdb_path(profile, ACME_PROFILES)
    with DuckDBExecutor(database) as executor:
        return run_full_audit(contracts, audit_profile, executor, profile)


def test_four_seeded_failures() -> None:
    """ACME demo data should trigger all four seeded failure modes."""
    result = _run_acme_audit()
    expected = json.loads(MOCK_RESULTS.read_text(encoding="utf-8"))

    assert result.verdict == "fail"
    phase_by_id = {phase.phase_id: phase for phase in result.phases}

    assert phase_by_id[1].status == "fail"
    crm = next(check for check in phase_by_id[1].checks if check.check_id == "audit.crm_coverage")
    assert crm.actual is not None
    assert crm.actual < expected["crm_coverage"]["sync_pct"] + 1

    assert phase_by_id[2].status == "fail"
    retention = next(
        check for check in phase_by_id[2].checks if check.check_id.endswith("behavioral_features")
    )
    assert retention.status == "fail"

    assert phase_by_id[3].status == "warn"
    swap = next(
        check for check in phase_by_id[3].checks if check.check_id == "audit.source_swap_volume"
    )
    assert swap.status == "warn"
    assert swap.actual == expected["source_swap"]["drift_pct"]

    assert phase_by_id[4].status == "fail"
    parity = next(
        check
        for check in phase_by_id[4].checks
        if check.check_id.startswith("cohort.source_parity")
    )
    assert parity.status == "fail"

    assert phase_by_id[5].status == "pass"
    assert phase_by_id[5].checks[0].evidence["risks"]
