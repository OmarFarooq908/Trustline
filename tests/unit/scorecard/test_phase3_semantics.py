"""Tests for Phase 3 semantics scorecard checks."""

from pathlib import Path

from tests.unit.scorecard.fake_executor import FakeExecutor
from trustline.config import Profile
from trustline.contracts.audit_profile import load_audit_profile
from trustline.scorecard.phase3_semantics import run_phase3_semantics

REPO_ROOT = Path(__file__).resolve().parents[3]
AUDIT_PROFILE = REPO_ROOT / "examples" / "acme_stream" / "audit_profile.yaml"


def test_run_phase3_skips_without_audit_profile(duckdb_profile: Profile) -> None:
    """Phase 3 should skip when no audit profile is provided."""
    result = run_phase3_semantics(None, FakeExecutor(), duckdb_profile)
    assert result.status == "skip"
    assert result.checks == ()


def test_run_phase3_warns_on_source_swap_drift_above_threshold(duckdb_profile: Profile) -> None:
    """Source swap volume drift should warn when above threshold (ACME failure #3)."""
    audit_profile = load_audit_profile(AUDIT_PROFILE)
    executor = FakeExecutor(
        {
            "audit.source_swap_volume": 11.0,
            "audit.score_distribution": 1.0,
        }
    )
    result = run_phase3_semantics(audit_profile, executor, duckdb_profile)

    assert result.phase_id == 3
    assert result.name == "Score Semantics"
    assert result.status == "warn"
    assert len(result.checks) == 2
    swap = next(check for check in result.checks if check.check_id == "audit.source_swap_volume")
    assert swap.status == "warn"
    assert swap.actual == 11.0
    assert swap.expected == 10.0


def test_run_phase3_includes_score_distribution_check(duckdb_profile: Profile) -> None:
    """Phase 3 should include the optional score distribution stability check."""
    audit_profile = load_audit_profile(AUDIT_PROFILE)
    executor = FakeExecutor(
        {
            "audit.source_swap_volume": 5.0,
            "audit.score_distribution": 1.0,
        }
    )
    result = run_phase3_semantics(audit_profile, executor, duckdb_profile)

    distribution = next(
        check for check in result.checks if check.check_id == "audit.score_distribution"
    )
    assert distribution.status == "pass"
    assert result.status == "pass"
