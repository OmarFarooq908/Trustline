"""Fake executor for scorecard unit tests."""

from __future__ import annotations

from typing import Any

from trustline.executors.base import CheckExpectation, CheckResult, CompiledCheck, result_from_rows


def metric_row(expect: CheckExpectation, value: float | int) -> dict[str, Any]:
    """Build a single-row SQL result for a check expectation kind."""
    if expect.kind == "min_count":
        return {"actual_count": value}
    if expect.kind == "min_retention_pct":
        return {"retention_pct": value}
    if expect.kind == "max_drift_pct":
        return {"drift_pct": value}
    if expect.kind == "min_sync_pct":
        return {"sync_pct": value}
    if expect.kind == "source_parity":
        return {"actual": value}
    if expect.kind == "positive_rate":
        return {"positive_rate": value}
    return {"value": value}


class FakeExecutor:
    """Executor stub that returns scripted metrics per check id."""

    def __init__(self, metrics: dict[str, float | int] | None = None) -> None:
        self.metrics = metrics or {}
        self.executed_checks: list[CompiledCheck] = []

    def execute(self, sql: str) -> list[dict[str, Any]]:
        return []

    def execute_check(self, check: CompiledCheck) -> CheckResult:
        self.executed_checks.append(check)
        metric = self.metrics.get(check.check_id)
        if metric is None:
            return result_from_rows(check, [])
        return result_from_rows(check, [metric_row(check.expect, metric)])
