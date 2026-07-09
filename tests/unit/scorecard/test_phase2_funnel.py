"""Tests for Phase 2 funnel scorecard checks."""

from pathlib import Path

from tests.unit.scorecard.fake_executor import FakeExecutor
from trustline.config import Profile
from trustline.contracts.loader import load_contract
from trustline.contracts.models import FunnelContract
from trustline.scorecard.phase2_funnel import run_phase2_funnel


def test_run_phase2_skips_without_funnel_contracts(duckdb_profile: Profile) -> None:
    """Phase 2 should skip when no funnel contracts are provided."""
    result = run_phase2_funnel([], FakeExecutor(), duckdb_profile)
    assert result.status == "skip"
    assert result.checks == ()


def test_run_phase2_fails_on_retention_below_threshold(
    acme_contracts_dir: Path,
    duckdb_profile: Profile,
) -> None:
    """Funnel retention should fail when a stage drops below its threshold (ACME failure #1)."""
    contract = load_contract(acme_contracts_dir / "training_positives.yaml")
    assert isinstance(contract, FunnelContract)

    executor = FakeExecutor(
        {
            "funnel.count.training_positives.source_donors": 2000,
            "funnel.retention.training_positives.app_identity_match": 35.0,
            "funnel.retention.training_positives.behavioral_features": 30.0,
        }
    )
    result = run_phase2_funnel([contract], executor, duckdb_profile)

    assert result.phase_id == 2
    assert result.name == "Population Funnel"
    assert result.status == "fail"
    assert len(result.checks) == 3
    retention = next(
        check for check in result.checks if check.check_id.endswith("app_identity_match")
    )
    assert retention.status == "fail"
    assert retention.actual == 35.0
    assert retention.expected == 40.0


def test_run_phase2_passes_when_counts_and_retention_meet_thresholds(
    acme_contracts_dir: Path,
    duckdb_profile: Profile,
) -> None:
    """Funnel checks should pass when all stage metrics meet contract thresholds."""
    contract = load_contract(acme_contracts_dir / "training_positives.yaml")
    assert isinstance(contract, FunnelContract)

    executor = FakeExecutor(
        {
            "funnel.count.training_positives.source_donors": 2000,
            "funnel.retention.training_positives.app_identity_match": 40.0,
            "funnel.retention.training_positives.behavioral_features": 25.0,
        }
    )
    result = run_phase2_funnel([contract], executor, duckdb_profile)
    assert result.status == "pass"
    assert all(check.status == "pass" for check in result.checks)
