"""Tests for Phase 1 pipeline scorecard checks."""

from pathlib import Path

from tests.unit.scorecard.fake_executor import FakeExecutor
from trustline.config import Profile
from trustline.contracts.audit_profile import load_audit_profile
from trustline.scorecard.phase1_pipeline import run_phase1_pipeline

REPO_ROOT = Path(__file__).resolve().parents[3]
AUDIT_PROFILE = REPO_ROOT / "examples" / "acme_stream" / "audit_profile.yaml"


def test_run_phase1_skips_without_audit_profile(duckdb_profile: Profile) -> None:
    """Phase 1 should skip when no audit profile is provided."""
    result = run_phase1_pipeline(None, FakeExecutor(), duckdb_profile)
    assert result.status == "skip"
    assert result.checks == ()


def test_run_phase1_fails_when_sync_pct_below_threshold(duckdb_profile: Profile) -> None:
    """CRM coverage should fail when sync_pct is below expect_sync_pct."""
    audit_profile = load_audit_profile(AUDIT_PROFILE)
    executor = FakeExecutor({"audit.crm_coverage": 26.67})
    result = run_phase1_pipeline(audit_profile, executor, duckdb_profile)

    assert result.phase_id == 1
    assert result.name == "Pipeline Truth"
    assert result.status == "fail"
    assert len(result.checks) == 1
    assert result.checks[0].check_id == "audit.crm_coverage"
    assert result.checks[0].actual == 26.67
    assert result.checks[0].expected == 95


def test_run_phase1_passes_when_sync_pct_meets_threshold(duckdb_profile: Profile) -> None:
    """CRM coverage should pass when sync_pct meets the audit profile threshold."""
    audit_profile = load_audit_profile(AUDIT_PROFILE)
    executor = FakeExecutor({"audit.crm_coverage": 96.0})
    result = run_phase1_pipeline(audit_profile, executor, duckdb_profile)

    assert result.status == "pass"
    assert result.checks[0].status == "pass"
