"""Phase 3 score semantics checks."""

from __future__ import annotations

from trustline.compiler.audit_profile import compile_audit_profile_checks
from trustline.config import Profile
from trustline.contracts.audit_profile import AuditProfile
from trustline.executors.base import Executor
from trustline.scorecard._common import aggregate_check_status, dialect_for_profile, execute_checks
from trustline.scorecard.types import PHASE_NAMES, PhaseResult


def run_phase3_semantics(
    audit_profile: AuditProfile | None,
    executor: Executor,
    profile: Profile,
) -> PhaseResult:
    """Run source swap volume and score distribution checks."""
    if audit_profile is None:
        return PhaseResult(phase_id=3, name=PHASE_NAMES[3], status="skip")

    dialect = dialect_for_profile(profile.target)
    checks = [
        check
        for check in compile_audit_profile_checks(audit_profile, profile, dialect)
        if check.phase == 3
    ]
    results = execute_checks(executor, checks)
    return PhaseResult(
        phase_id=3,
        name=PHASE_NAMES[3],
        status=aggregate_check_status(results),
        checks=tuple(results),
    )
