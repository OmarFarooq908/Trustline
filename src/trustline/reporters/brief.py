"""Leadership brief reporter."""

from __future__ import annotations

from trustline.scorecard.phase5_brief import run_phase5_brief
from trustline.scorecard.types import ScorecardResult


def render_brief(result: ScorecardResult) -> str:
    """Render the Phase 5 leadership brief as markdown."""
    sql_phases = tuple(phase for phase in result.phases if phase.phase_id <= 4)
    brief_phase = run_phase5_brief(sql_phases)
    if not brief_phase.checks:
        return "# Leadership Brief\n\n_No findings to summarize._\n"

    evidence = brief_phase.checks[0].evidence
    risks = evidence.get("risks", [])
    actions = evidence.get("actions", [])

    lines = [
        "# Leadership Brief",
        "",
        f"**Overall verdict:** {result.verdict.upper()}",
        "",
        "## Top Risks",
        "",
    ]

    if risks:
        for index, risk in enumerate(risks, start=1):
            lines.append(
                f"{index}. **{risk['phase']}** — {risk['risk']} "
                f"(`{risk['check_id']}`, {risk['status'].upper()})"
            )
    else:
        lines.append("_No failing or warning checks detected._")

    lines.extend(["", "## Recommended Actions", ""])
    if actions:
        for index, action in enumerate(actions, start=1):
            lines.append(f"{index}. {action}")
    else:
        lines.append("_No remediation actions required._")

    return "\n".join(lines).rstrip() + "\n"
