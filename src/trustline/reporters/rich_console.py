"""Rich terminal scorecard reporter."""

from __future__ import annotations

import os
import shutil

from rich.console import Console
from rich.table import Table
from rich.text import Text

from trustline.reporters.scoring import (
    phase_score,
    recommendation_for,
    trust_score,
    verdict_headline,
)
from trustline.scorecard.types import PhaseResult, ScorecardResult

_STATUS_SYMBOLS = {"pass": "✅", "warn": "⚠️", "fail": "❌", "skip": "⏭️"}


def _color_enabled(*, no_color: bool) -> bool:
    if no_color:
        return False
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("FORCE_COLOR"):
        return True
    return Console().is_terminal


def _score_bar(score: int, *, width: int = 10) -> str:
    filled = round(width * score / 100)
    return "█" * filled + "░" * (width - filled)


def _phase_status_label(phase: PhaseResult) -> str:
    symbol = _STATUS_SYMBOLS.get(phase.status, "")
    label = phase.status.upper()
    return f"{symbol} {label}".strip()


def _phase_annotation(phase: PhaseResult) -> str | None:
    """Return a short note for the worst failing check in a phase."""
    if phase.status not in {"fail", "warn"}:
        return None
    for check in phase.checks:
        if check.status not in {"fail", "warn"}:
            continue
        if check.check_id == "audit.crm_coverage" and isinstance(check.actual, (int, float)):
            missing = round(100 - float(check.actual))
            return f"← {missing}% of queued contacts missing from mirror"
        if check.actual is not None and check.expected is not None:
            return f"← {check.check_id} reported {check.status}"
    return None


def render_scorecard_console(
    result: ScorecardResult,
    *,
    title: str,
    no_color: bool = False,
) -> None:
    """Print a Rich scorecard summary to stdout."""
    score = trust_score(result)
    use_color = _color_enabled(no_color=no_color)
    width = min(100, shutil.get_terminal_size(fallback=(100, 24)).columns)
    console = Console(
        width=width,
        color_system="standard" if use_color else None,
        no_color=not use_color,
    )

    console.print(f"Trustline Audit — {title}\n")
    bar = _score_bar(score)
    headline = verdict_headline(result.verdict)
    console.print(f"Overall Trust Score  {bar}  {score}/100  {headline}\n")

    table = Table(show_header=True, header_style="bold" if use_color else None)
    table.add_column("Phase", style="cyan" if use_color else None, no_wrap=True)
    table.add_column("Score", justify="right")
    table.add_column("Status", overflow="fold")

    for phase in result.phases:
        if phase.phase_id > 5:
            continue
        annotation = _phase_annotation(phase)
        status_text = _phase_status_label(phase)
        if annotation:
            status_text = f"{status_text}  {annotation}"
        table.add_row(phase.name, str(phase_score(phase)), status_text)

    console.print(table)
    console.print()
    console.print(Text(recommendation_for(result), style="bold" if use_color else None))
