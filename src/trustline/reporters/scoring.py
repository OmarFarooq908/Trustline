"""Trust score and recommendation helpers for scorecard reporters."""

from __future__ import annotations

from trustline.scorecard.types import PhaseResult, ScorecardResult


def phase_score(phase: PhaseResult) -> int:
    """Derive a 0–100 score from pass/fail/warn check counts in a phase."""
    if phase.status == "skip":
        return 100
    if not phase.checks:
        return 100
    passed = sum(1 for check in phase.checks if check.status == "pass")
    return round(100 * passed / len(phase.checks))


def trust_score(result: ScorecardResult) -> int:
    """Overall trust score from SQL phases (1–4), excluding the leadership brief."""
    scored = [phase for phase in result.phases if phase.phase_id <= 4 and phase.status != "skip"]
    if not scored:
        return 100
    return round(sum(phase_score(phase) for phase in scored) / len(scored))


def recommendation_for(result: ScorecardResult) -> str:
    """Plain-language deployment recommendation from the scorecard outcome."""
    if result.verdict == "pass":
        return "All contract checks passed — safe to proceed with deployment."
    if result.verdict == "warn":
        return "Review warnings before deployment; contracts reported non-blocking issues."

    phase5 = next((phase for phase in result.phases if phase.phase_id == 5), None)
    if phase5 and phase5.checks:
        actions = phase5.checks[0].evidence.get("actions", [])
        if isinstance(actions, list) and actions:
            first = actions[0]
            if isinstance(first, str) and first:
                return first

    return "Block deployment until failing contract checks pass."


def verdict_headline(verdict: str) -> str:
    """Short verdict line for console and JSON output."""
    if verdict == "pass":
        return "PASS — safe to deploy"
    if verdict == "warn":
        return "WARN — review before deploy"
    return "FAIL — block deploy"
