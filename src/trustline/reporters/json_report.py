"""JSON scorecard reporter."""

from __future__ import annotations

from typing import Any, cast

from trustline.reporters.redact import redact_secrets
from trustline.reporters.scoring import phase_score, recommendation_for, trust_score
from trustline.scorecard.types import ScorecardResult


def _format_check(
    check_id: str, status: str, actual: Any, expected: Any, evidence: Any
) -> dict[str, Any]:
    """Build a JSON check object with percentage fields when appropriate."""
    payload: dict[str, Any] = {
        "id": check_id,
        "status": status,
        "evidence": redact_secrets(evidence),
    }
    if actual is not None:
        if "retention" in check_id or check_id.endswith("_pct") or "sync_pct" in str(evidence):
            payload["actual_pct"] = actual
        elif "positive_rate" in check_id:
            payload["actual_rate"] = actual
        elif "drift" in check_id:
            payload["actual_pct"] = actual
        else:
            payload["actual"] = actual
    if expected is not None:
        if "retention" in check_id:
            payload["expected_pct"] = expected
        elif "positive_rate" in check_id:
            payload["expected_rate"] = expected
        elif "drift" in check_id or "sync" in check_id:
            payload["expected_pct"] = expected
        else:
            payload["expected"] = expected
    return payload


def render_scorecard_json(result: ScorecardResult) -> dict[str, Any]:
    """Render a scorecard as a JSON-serializable dictionary."""
    phases: list[dict[str, Any]] = []
    for phase in result.phases:
        checks = [
            _format_check(
                check.check_id,
                check.status,
                check.actual,
                check.expected,
                check.evidence,
            )
            for check in phase.checks
        ]
        phases.append(
            {
                "id": phase.phase_id,
                "name": phase.name,
                "status": phase.status,
                "score": phase_score(phase),
                "checks": checks,
            }
        )

    payload: dict[str, Any] = {
        "verdict": result.verdict,
        "trust_score": trust_score(result),
        "recommendation": recommendation_for(result),
        "generated_at": result.generated_at.isoformat(),
        "phases": phases,
        "evidence": result.evidence,
    }
    return cast(dict[str, Any], redact_secrets(payload))
