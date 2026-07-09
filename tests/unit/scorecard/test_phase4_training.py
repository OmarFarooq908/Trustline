"""Tests for Phase 4 training autopsy scorecard checks."""

from pathlib import Path

from tests.unit.scorecard.fake_executor import FakeExecutor
from trustline.config import Profile
from trustline.contracts.loader import load_contract
from trustline.contracts.models import CohortManifest
from trustline.scorecard.phase4_training import run_phase4_training


def test_run_phase4_skips_without_cohort_contracts(duckdb_profile: Profile) -> None:
    """Phase 4 should skip when no cohort manifests are provided."""
    result = run_phase4_training([], FakeExecutor(), duckdb_profile)
    assert result.status == "skip"
    assert result.checks == ()


def test_run_phase4_fails_on_training_scoring_source_mismatch(
    acme_contracts_dir: Path,
    duckdb_profile: Profile,
) -> None:
    """Cohort source parity fails when training and scoring sources differ."""
    contract = load_contract(acme_contracts_dir / "propensity_training_cohort_q2.yaml")
    assert isinstance(contract, CohortManifest)

    executor = FakeExecutor(
        {
            "cohort.source_parity.propensity-training-cohort-q2": 0.0,
            "cohort.positive_rate.propensity-training-cohort-q2": 0.12,
        }
    )
    result = run_phase4_training([contract], executor, duckdb_profile)

    assert result.phase_id == 4
    assert result.name == "Training Autopsy"
    assert result.status == "fail"
    assert len(result.checks) == 2
    parity = next(
        check for check in result.checks if check.check_id.startswith("cohort.source_parity")
    )
    assert parity.status == "fail"
    assert parity.actual == 0.0


def test_run_phase4_includes_positive_rate_tolerance_check(
    acme_contracts_dir: Path,
    duckdb_profile: Profile,
) -> None:
    """Positive rate should pass when within the contract tolerance."""
    contract = load_contract(acme_contracts_dir / "propensity_training_cohort_q2.yaml")
    assert isinstance(contract, CohortManifest)

    executor = FakeExecutor(
        {
            "cohort.source_parity.propensity-training-cohort-q2": 1.0,
            "cohort.positive_rate.propensity-training-cohort-q2": 0.13,
        }
    )
    result = run_phase4_training([contract], executor, duckdb_profile)

    rate = next(
        check for check in result.checks if check.check_id.startswith("cohort.positive_rate")
    )
    assert rate.status == "pass"
    assert rate.actual == 0.13
    assert rate.expected == 0.12
    assert result.status == "pass"
