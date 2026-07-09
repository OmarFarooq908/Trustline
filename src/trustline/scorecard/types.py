"""Scorecard result types."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Literal

from trustline.executors.base import CheckResult

PhaseStatus = Literal["pass", "fail", "warn", "skip"]
ScorecardVerdict = Literal["pass", "fail", "warn"]

PHASE_NAMES: dict[int, str] = {
    1: "Pipeline Truth",
    2: "Population Funnel",
    3: "Score Semantics",
    4: "Training Autopsy",
    5: "Leadership Brief",
}


@dataclass(frozen=True)
class PhaseResult:
    """Outcome of a single scorecard phase."""

    phase_id: int
    name: str
    status: PhaseStatus
    checks: tuple[CheckResult, ...] = ()


@dataclass(frozen=True)
class ScorecardResult:
    """Aggregate outcome of a trust audit."""

    verdict: ScorecardVerdict
    phases: tuple[PhaseResult, ...]
    evidence: dict[str, Any] = field(default_factory=dict)
    generated_at: datetime = field(default_factory=lambda: datetime.now(tz=UTC))
