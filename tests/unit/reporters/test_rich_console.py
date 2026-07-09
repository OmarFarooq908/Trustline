"""Tests for Rich console scorecard reporter."""

from io import StringIO

from rich.console import Console

from trustline.executors.base import CheckResult
from trustline.reporters.rich_console import _phase_annotation, render_scorecard_console
from trustline.scorecard.types import PhaseResult, ScorecardResult


def test_phase_annotation_for_crm_coverage() -> None:
    """CRM coverage failures should include a mirror-gap note."""
    phase = PhaseResult(
        phase_id=1,
        name="Pipeline Truth",
        status="fail",
        checks=(
            CheckResult(
                check_id="audit.crm_coverage",
                status="fail",
                actual=26.67,
                expected=95.0,
                evidence={},
            ),
        ),
    )
    assert _phase_annotation(phase) == "note: 73% of queued contacts missing from mirror"


def test_render_scorecard_console_includes_trust_score() -> None:
    """Console output should include trust score and phase table headers."""
    buffer = StringIO()
    result = ScorecardResult(
        verdict="fail",
        phases=(
            PhaseResult(
                phase_id=1,
                name="Pipeline Truth",
                status="fail",
                checks=(
                    CheckResult(
                        check_id="audit.crm_coverage",
                        status="fail",
                        actual=26.67,
                        expected=95.0,
                        evidence={},
                    ),
                ),
            ),
            PhaseResult(phase_id=5, name="Leadership Brief", status="pass", checks=()),
        ),
    )

    def _console_factory(*_args: object, **_kwargs: object) -> Console:
        return Console(
            file=buffer, width=120, force_terminal=True, color_system=None, no_color=True
        )

    from unittest.mock import patch

    with patch("trustline.reporters.rich_console.Console", side_effect=_console_factory):
        render_scorecard_console(result, title="ACME Stream", no_color=True)

    output = buffer.getvalue()
    assert "Overall Trust Score" in output
    assert "Pipeline Truth" in output
    assert "FAIL — block deploy" in output
    assert "73%" in output
