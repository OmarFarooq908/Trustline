"""Markdown scorecard reporter."""

from __future__ import annotations

from trustline.scorecard.types import PhaseResult, ScorecardResult


def _status_label(status: str) -> str:
    return status.upper()


def _phase_summary_lines(phases: tuple[PhaseResult, ...]) -> list[str]:
    lines: list[str] = []
    for phase in phases:
        dots = "." * max(1, 34 - len(phase.name))
        lines.append(f"Phase {phase.phase_id} {phase.name} {dots} {_status_label(phase.status)}")
    return lines


def _count_outcomes(phases: tuple[PhaseResult, ...]) -> tuple[int, int]:
    failures = sum(1 for phase in phases if phase.status == "fail")
    warnings = sum(1 for phase in phases if phase.status == "warn")
    return failures, warnings


def _verdict_summary(result: ScorecardResult) -> str:
    failures, warnings = _count_outcomes(result.phases)
    if result.verdict == "pass":
        return "PASS"
    if result.verdict == "warn":
        return f"WARN ({warnings} warning{'s' if warnings != 1 else ''})"
    parts: list[str] = [f"FAIL ({failures} failure{'s' if failures != 1 else ''}"]
    if warnings:
        parts[0] += f", {warnings} warning{'s' if warnings != 1 else ''}"
    parts[0] += ")"
    return parts[0]


def render_scorecard(result: ScorecardResult, *, title: str = "Trustline Audit") -> str:
    """Render a human-readable markdown scorecard report."""
    lines = [
        f"# {title}",
        "",
        f"**Verdict:** {_verdict_summary(result)}",
        "",
        f"**Generated:** {result.generated_at.isoformat()}",
        "",
        "## Phase Summary",
        "",
        "```",
        *_phase_summary_lines(result.phases),
        "```",
        "",
        "## Details",
        "",
    ]

    for phase in result.phases:
        if phase.status == "skip":
            continue
        lines.extend([f"### Phase {phase.phase_id}: {phase.name}", ""])
        if not phase.checks:
            lines.extend(["_No checks executed._", ""])
            continue
        for check in phase.checks:
            actual = "n/a" if check.actual is None else str(check.actual)
            expected = "n/a" if check.expected is None else str(check.expected)
            lines.append(
                f"- **{check.check_id}** — {check.status.upper()} "
                f"(actual: {actual}, expected: {expected})"
            )
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"
