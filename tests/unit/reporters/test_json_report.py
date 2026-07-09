"""Tests for JSON scorecard reporter."""

from pathlib import Path

from tests.unit.scorecard.fake_executor import FakeExecutor
from trustline.config import Profile
from trustline.contracts.audit_profile import load_audit_profile
from trustline.contracts.loader import load_contract
from trustline.contracts.models import CohortManifest, FunnelContract
from trustline.executors.base import CheckResult
from trustline.reporters.json_report import render_scorecard_json
from trustline.scorecard.orchestrator import run_audit
from trustline.scorecard.types import PhaseResult, ScorecardResult

REPO_ROOT = Path(__file__).resolve().parents[3]
AUDIT_PROFILE = REPO_ROOT / "examples" / "acme_stream" / "audit_profile.yaml"


def _acme_fail_result(acme_contracts_dir: Path, duckdb_profile: Profile) -> ScorecardResult:
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


def test_render_scorecard_json_matches_cli_contract(
    acme_contracts_dir: Path,
    duckdb_profile: Profile,
) -> None:
    """JSON output should include verdict, generated_at, and phase check details."""
    result = _acme_fail_result(acme_contracts_dir, duckdb_profile)
    payload = render_scorecard_json(result)

    assert payload["verdict"] == "fail"
    assert "generated_at" in payload
    assert len(payload["phases"]) == 4
    funnel_phase = next(phase for phase in payload["phases"] if phase["id"] == 2)
    retention = next(
        check for check in funnel_phase["checks"] if check["id"].endswith("app_identity_match")
    )
    assert retention["status"] == "fail"
    assert retention["actual_pct"] == 35.0
    assert retention["expected_pct"] == 40.0


def test_render_scorecard_json_redacts_connection_strings() -> None:
    """Evidence embedded in checks should have secrets redacted."""
    check = CheckResult(
        check_id="audit.crm_coverage",
        status="fail",
        actual=10.0,
        expected=95.0,
        evidence={
            "rows": [{"dsn": "snowflake://user:secret@acct/db"}],
            "evidence_key": "crm_coverage",
        },
    )
    phase = PhaseResult(phase_id=1, name="Pipeline Truth", status="fail", checks=(check,))
    result = ScorecardResult(verdict="fail", phases=(phase,))
    payload = render_scorecard_json(result)

    rendered = str(payload)
    assert "secret" not in rendered
    assert "[REDACTED]" in rendered
