"""Phase 4 training autopsy checks."""

from __future__ import annotations

from trustline.compiler.cohort import compile_cohort_checks
from trustline.config import Profile
from trustline.contracts.models import CohortManifest
from trustline.executors.base import CompiledCheck, Executor
from trustline.scorecard._common import aggregate_check_status, dialect_for_profile, execute_checks
from trustline.scorecard.types import PHASE_NAMES, PhaseResult


def run_phase4_training(
    contracts: list[CohortManifest],
    executor: Executor,
    profile: Profile,
) -> PhaseResult:
    """Run cohort source parity and positive rate checks."""
    if not contracts:
        return PhaseResult(phase_id=4, name=PHASE_NAMES[4], status="skip")

    dialect = dialect_for_profile(profile.target)
    compiled: list[CompiledCheck] = []
    for contract in contracts:
        compiled.extend(compile_cohort_checks(contract, profile, dialect))

    results = execute_checks(executor, compiled)
    return PhaseResult(
        phase_id=4,
        name=PHASE_NAMES[4],
        status=aggregate_check_status(results),
        checks=tuple(results),
    )
