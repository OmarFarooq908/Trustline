"""Tests for scorecard orchestrator."""

from pathlib import Path

from tests.unit.scorecard.fake_executor import FakeExecutor
from trustline.config import Profile
from trustline.contracts.audit_profile import load_audit_profile
from trustline.contracts.loader import load_contract
from trustline.contracts.models import CohortManifest, FunnelContract
from trustline.scorecard.orchestrator import run_audit
from trustline.scorecard.types import ScorecardResult

REPO_ROOT = Path(__file__).resolve().parents[3]
AUDIT_PROFILE = REPO_ROOT / "examples" / "acme_stream" / "audit_profile.yaml"


def _acme_contracts(acme_contracts_dir: Path) -> list[FunnelContract | CohortManifest]:
    funnel = load_contract(acme_contracts_dir / "training_positives.yaml")
    cohort = load_contract(acme_contracts_dir / "propensity_training_cohort_q2.yaml")
    assert isinstance(funnel, FunnelContract)
    assert isinstance(cohort, CohortManifest)
    return [funnel, cohort]


def test_run_audit_executes_phases_one_through_four(
    acme_contracts_dir: Path,
    duckdb_profile: Profile,
) -> None:
    """run_audit should execute phases 1–4 and return a ScorecardResult."""
    audit_profile = load_audit_profile(AUDIT_PROFILE)
    contracts = _acme_contracts(acme_contracts_dir)
    executor = FakeExecutor(
        {
            "audit.crm_coverage": 96.0,
            "funnel.count.training_positives.source_donors": 2000,
            "funnel.retention.training_positives.app_identity_match": 40.0,
            "funnel.retention.training_positives.behavioral_features": 25.0,
            "audit.source_swap_volume": 5.0,
            "audit.score_distribution": 1.0,
            "cohort.source_parity.propensity-training-cohort-q2": 1.0,
            "cohort.positive_rate.propensity-training-cohort-q2": 0.12,
        }
    )

    result = run_audit(contracts, audit_profile, executor, duckdb_profile)

    assert isinstance(result, ScorecardResult)
    assert len(result.phases) == 4
    assert [phase.phase_id for phase in result.phases] == [1, 2, 3, 4]
    assert result.verdict == "pass"
    assert set(result.evidence) == {
        "Pipeline Truth",
        "Population Funnel",
        "Score Semantics",
        "Training Autopsy",
    }


def test_run_audit_verdict_fail_when_any_phase_fails(
    acme_contracts_dir: Path,
    duckdb_profile: Profile,
) -> None:
    """Overall verdict should be fail when any phase fails."""
    audit_profile = load_audit_profile(AUDIT_PROFILE)
    contracts = _acme_contracts(acme_contracts_dir)
    executor = FakeExecutor(
        {
            "audit.crm_coverage": 26.67,
            "funnel.count.training_positives.source_donors": 2000,
            "funnel.retention.training_positives.app_identity_match": 35.0,
            "funnel.retention.training_positives.behavioral_features": 30.0,
            "audit.source_swap_volume": 11.0,
            "audit.score_distribution": 1.0,
            "cohort.source_parity.propensity-training-cohort-q2": 0.0,
            "cohort.positive_rate.propensity-training-cohort-q2": 0.12,
        }
    )

    result = run_audit(contracts, audit_profile, executor, duckdb_profile)

    assert result.verdict == "fail"
    assert result.phases[0].status == "fail"
    assert result.phases[1].status == "fail"
    assert result.phases[2].status == "warn"
    assert result.phases[3].status == "fail"


def test_run_audit_verdict_warn_when_only_warnings(
    acme_contracts_dir: Path,
    duckdb_profile: Profile,
) -> None:
    """Overall verdict should be warn when no phase fails but warnings exist."""
    audit_profile = load_audit_profile(AUDIT_PROFILE)
    contracts = _acme_contracts(acme_contracts_dir)
    executor = FakeExecutor(
        {
            "audit.crm_coverage": 96.0,
            "funnel.count.training_positives.source_donors": 2000,
            "funnel.retention.training_positives.app_identity_match": 40.0,
            "funnel.retention.training_positives.behavioral_features": 25.0,
            "audit.source_swap_volume": 11.0,
            "audit.score_distribution": 1.0,
            "cohort.source_parity.propensity-training-cohort-q2": 1.0,
            "cohort.positive_rate.propensity-training-cohort-q2": 0.12,
        }
    )

    result = run_audit(contracts, audit_profile, executor, duckdb_profile)

    assert result.verdict == "warn"
    assert all(phase.status != "fail" for phase in result.phases)
    assert any(phase.status == "warn" for phase in result.phases)
