"""Tests for scorecard scoring helpers."""

from trustline.executors.base import CheckResult
from trustline.reporters.scoring import phase_score, recommendation_for, trust_score
from trustline.scorecard.types import PhaseResult, ScorecardResult


def test_phase_score_all_pass() -> None:
    """All passing checks should score 100."""
    phase = PhaseResult(
        phase_id=1,
        name="Pipeline Truth",
        status="pass",
        checks=(
            CheckResult(check_id="a", status="pass", actual=1, expected=1, evidence={}),
            CheckResult(check_id="b", status="pass", actual=1, expected=1, evidence={}),
        ),
    )
    assert phase_score(phase) == 100


def test_phase_score_mixed_checks() -> None:
    """Mixed pass/fail checks should score proportionally."""
    phase = PhaseResult(
        phase_id=2,
        name="Population Funnel",
        status="fail",
        checks=(
            CheckResult(check_id="a", status="pass", actual=1, expected=1, evidence={}),
            CheckResult(check_id="b", status="fail", actual=0, expected=1, evidence={}),
        ),
    )
    assert phase_score(phase) == 50


def test_trust_score_averages_sql_phases() -> None:
    """Trust score should average phases 1–4 and ignore the leadership brief."""
    phases = (
        PhaseResult(phase_id=1, name="P1", status="fail", checks=(_check("fail"),)),
        PhaseResult(phase_id=2, name="P2", status="pass", checks=(_check("pass"),)),
        PhaseResult(phase_id=3, name="P3", status="pass", checks=(_check("pass"),)),
        PhaseResult(phase_id=4, name="P4", status="pass", checks=(_check("pass"),)),
        PhaseResult(phase_id=5, name="Brief", status="pass", checks=()),
    )
    result = ScorecardResult(verdict="fail", phases=phases)
    assert trust_score(result) == 75


def test_recommendation_uses_leadership_brief_action() -> None:
    """Failed audits should surface the first leadership brief action."""
    phase5 = PhaseResult(
        phase_id=5,
        name="Leadership Brief",
        status="pass",
        checks=(
            CheckResult(
                check_id="brief.leadership_summary",
                status="pass",
                actual=1,
                expected=0,
                evidence={"actions": ["Review CRM ETL sync lag"]},
            ),
        ),
    )
    phases = (
        PhaseResult(phase_id=1, name="P1", status="fail", checks=(_check("fail"),)),
        phase5,
    )
    result = ScorecardResult(verdict="fail", phases=phases)
    assert recommendation_for(result) == "Review CRM ETL sync lag"


def _check(status: str) -> CheckResult:
    return CheckResult(check_id="x", status=status, actual=1, expected=1, evidence={})
