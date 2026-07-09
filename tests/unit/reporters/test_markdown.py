"""Tests for markdown scorecard reporter."""

from pathlib import Path

from tests.unit.scorecard.fake_executor import FakeExecutor
from trustline.config import Profile
from trustline.contracts.audit_profile import load_audit_profile
from trustline.contracts.loader import load_contract
from trustline.contracts.models import CohortManifest, FunnelContract
from trustline.reporters.markdown import render_scorecard
from trustline.scorecard.orchestrator import run_audit

REPO_ROOT = Path(__file__).resolve().parents[3]
AUDIT_PROFILE = REPO_ROOT / "examples" / "acme_stream" / "audit_profile.yaml"


def _acme_fail_result(acme_contracts_dir: Path, duckdb_profile: Profile):
    audit_profile = load_audit_profile(AUDIT_PROFILE)
    funnel = load_contract(acme_contracts_dir / "training_positives.yaml")
    cohort = load_contract(acme_contracts_dir / "propensity_training_cohort_q2.yaml")
    assert isinstance(funnel, FunnelContract)
    assert isinstance(cohort, CohortManifest)
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
    return run_audit([funnel, cohort], audit_profile, executor, duckdb_profile)


def test_render_scorecard_includes_verdict_and_phase_summary(
    acme_contracts_dir: Path,
    duckdb_profile: Profile,
) -> None:
    """Markdown report should include verdict and per-phase summary lines."""
    result = _acme_fail_result(acme_contracts_dir, duckdb_profile)
    markdown = render_scorecard(result, title="Trustline Audit — ACME Stream")

    assert "# Trustline Audit — ACME Stream" in markdown
    assert "**Verdict:** FAIL" in markdown
    assert "Phase 1 Pipeline Truth" in markdown
    assert "FAIL" in markdown
    assert "Phase 2 Population Funnel" in markdown
    assert "funnel.retention.training_positives.app_identity_match" in markdown


def test_render_scorecard_lists_check_details(
    acme_contracts_dir: Path,
    duckdb_profile: Profile,
) -> None:
    """Markdown details section should list individual check outcomes."""
    result = _acme_fail_result(acme_contracts_dir, duckdb_profile)
    markdown = render_scorecard(result)

    assert "## Details" in markdown
    assert "audit.crm_coverage" in markdown
    assert "cohort.source_parity.propensity-training-cohort-q2" in markdown
