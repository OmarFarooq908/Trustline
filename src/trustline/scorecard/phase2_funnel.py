"""Phase 2 population funnel checks."""

from __future__ import annotations

from trustline.compiler.funnel import compile_funnel_checks
from trustline.config import Profile
from trustline.contracts.models import FunnelContract
from trustline.executors.base import CompiledCheck, Executor
from trustline.scorecard._common import aggregate_check_status, dialect_for_profile, execute_checks
from trustline.scorecard.types import PHASE_NAMES, PhaseResult


def run_phase2_funnel(
    contracts: list[FunnelContract],
    executor: Executor,
    profile: Profile,
) -> PhaseResult:
    """Run funnel stage count and retention checks."""
    if not contracts:
        return PhaseResult(phase_id=2, name=PHASE_NAMES[2], status="skip")

    dialect = dialect_for_profile(profile.target)
    compiled: list[CompiledCheck] = []
    for contract in contracts:
        compiled.extend(compile_funnel_checks(contract, profile, dialect))

    results = execute_checks(executor, compiled)
    return PhaseResult(
        phase_id=2,
        name=PHASE_NAMES[2],
        status=aggregate_check_status(results),
        checks=tuple(results),
    )
