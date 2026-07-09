"""Tests for audit profile loading and compilation."""

from pathlib import Path

from trustline.compiler.audit_profile import compile_audit_profile_checks
from trustline.config import Profile
from trustline.contracts.audit_profile import load_audit_profile

REPO_ROOT = Path(__file__).resolve().parents[3]
AUDIT_PROFILE = REPO_ROOT / "examples" / "acme_stream" / "audit_profile.yaml"


def test_load_audit_profile_acme_example() -> None:
    """ACME audit profile example should load and validate."""
    profile_doc = load_audit_profile(AUDIT_PROFILE)
    assert profile_doc.crm_coverage.expect_sync_pct == 95
    assert profile_doc.source_swap.migration.from_source == "LegacyPlayer"


def test_compile_audit_profile_checks_phases(duckdb_profile: Profile) -> None:
    """Audit profile should compile Phase 1 and Phase 3 checks."""
    profile_doc = load_audit_profile(AUDIT_PROFILE)
    checks = compile_audit_profile_checks(profile_doc, duckdb_profile, "duckdb")
    assert len(checks) == 3
    phases = {check.phase for check in checks}
    assert phases == {1, 3}
    kinds = {check.expect.kind for check in checks}
    assert kinds == {"min_sync_pct", "max_drift_pct", "min_count"}


def test_compile_audit_profile_resolves_refs(duckdb_profile: Profile) -> None:
    """Compiled audit profile SQL should resolve ACME table refs."""
    profile_doc = load_audit_profile(AUDIT_PROFILE)
    checks = compile_audit_profile_checks(profile_doc, duckdb_profile, "duckdb")
    combined = "\n".join(check.sql for check in checks)
    assert "main.crm_push_queue" in combined
    assert "main.crm_contacts_mirror" in combined
    assert "main.user_events_silver" in combined
    assert "LegacyPlayer" in combined
    assert "NewPlayer" in combined
