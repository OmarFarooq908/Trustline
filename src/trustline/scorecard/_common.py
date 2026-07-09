"""Shared scorecard execution helpers."""

from __future__ import annotations

from trustline.executors.base import CheckResult, CompiledCheck, Executor
from trustline.scorecard.types import PhaseStatus, ScorecardVerdict


def dialect_for_profile(target: str) -> str:
    """Map a profile target to a SQL template dialect."""
    if target == "snowflake":
        return "snowflake"
    return "duckdb"


def execute_checks(executor: Executor, checks: list[CompiledCheck]) -> list[CheckResult]:
    """Execute compiled checks and return results in order."""
    return [executor.execute_check(check) for check in checks]


def aggregate_check_status(checks: list[CheckResult]) -> PhaseStatus:
    """Derive phase status from individual check results."""
    if not checks:
        return "skip"
    if any(check.status == "fail" for check in checks):
        return "fail"
    if any(check.status == "warn" for check in checks):
        return "warn"
    return "pass"


def aggregate_verdict(phases: list[PhaseStatus]) -> ScorecardVerdict:
    """Derive overall scorecard verdict from phase statuses."""
    active = [status for status in phases if status != "skip"]
    if not active:
        return "pass"
    if any(status == "fail" for status in active):
        return "fail"
    if any(status == "warn" for status in active):
        return "warn"
    return "pass"
