"""Tests for Phase 5 leadership brief."""

from pathlib import Path

from tests.unit.scorecard.fake_executor import FakeExecutor
from trustline.config import Profile
from trustline.contracts.audit_profile import load_audit_profile
from trustline.contracts.loader import load_contract
from trustline.contracts.models import CohortManifest, FunnelContract
from trustline.reporters.brief import render_brief
from trustline.scorecard.orchestrator import run_audit
from trustline.scorecard.phase5_brief import run_phase5_brief
from trustline.scorecard.types import ScorecardResult

REPO_ROOT = Path(__file__).resolve().parents[3]
AUDIT_PROFILE = REPO_ROOT / "examples" / "acme_stream" / "audit_profile.yaml"


def _acme_fail_phases(acme_contracts_dir: Path, duckdb_profile: Profile):
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
    return run_audit([funnel, cohort], audit_profile, executor, duckdb_profile).phases


def test_run_phase5_brief_aggregates_prior_phases_without_sql(
    acme_contracts_dir: Path,
    duckdb_profile: Profile,
) -> None:
    """Phase 5 should summarize prior phases without executing SQL checks."""
    phases = _acme_fail_phases(acme_contracts_dir, duckdb_profile)
    brief = run_phase5_brief(phases)

    assert brief.phase_id == 5
    assert brief.name == "Leadership Brief"
    assert brief.status == "pass"
    assert len(brief.checks) == 1
    evidence = brief.checks[0].evidence
    assert len(evidence["risks"]) >= 3
    assert len(evidence["actions"]) >= 3


def test_run_phase5_brief_lists_top_risks_and_actions(
    acme_contracts_dir: Path,
    duckdb_profile: Profile,
) -> None:
    """Leadership brief should surface risks and recommended actions."""
    phases = _acme_fail_phases(acme_contracts_dir, duckdb_profile)
    brief = run_phase5_brief(phases)
    risks = brief.checks[0].evidence["risks"]
    actions = brief.checks[0].evidence["actions"]

    check_ids = {risk["check_id"] for risk in risks}
    assert "audit.crm_coverage" in check_ids
    assert "cohort.source_parity.propensity-training-cohort-q2" in check_ids
    assert any("CRM ETL" in action for action in actions)
    assert any("features_training" in action for action in actions)


def test_render_brief_produces_markdown_summary(
    acme_contracts_dir: Path,
    duckdb_profile: Profile,
) -> None:
    """Brief reporter should render markdown with risks and actions sections."""
    phases = _acme_fail_phases(acme_contracts_dir, duckdb_profile)
    result = ScorecardResult(verdict="fail", phases=phases)
    markdown = render_brief(result)

    assert "# Leadership Brief" in markdown
    assert "## Top Risks" in markdown
    assert "## Recommended Actions" in markdown
    assert "Population funnel retention" in markdown
