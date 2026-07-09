"""Warehouse executor protocol and check result types."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, Protocol

CheckStatus = Literal["pass", "fail", "warn"]
ExpectationKind = Literal[
    "min_count",
    "min_retention_pct",
    "max_drift_pct",
    "min_sync_pct",
    "source_parity",
]


@dataclass(frozen=True)
class CheckExpectation:
    """Expected outcome for a compiled SQL check."""

    kind: ExpectationKind
    value: float
    tolerance: float | None = None


@dataclass(frozen=True)
class CompiledCheck:
    """SQL check ready for warehouse execution."""

    check_id: str
    phase: int
    sql: str
    expect: CheckExpectation
    evidence_key: str


@dataclass(frozen=True)
class CheckResult:
    """Outcome of executing a single check."""

    check_id: str
    status: CheckStatus
    actual: float | int | None
    expected: float | int | None
    evidence: dict[str, Any]


class Executor(Protocol):
    """Warehouse adapter that runs compiled SQL checks."""

    def execute(self, sql: str) -> list[dict[str, Any]]:
        """Execute SQL and return rows as dictionaries."""
        ...

    def execute_check(self, check: CompiledCheck) -> CheckResult:
        """Execute a compiled check and evaluate the result."""
        ...


def extract_metric(rows: list[dict[str, Any]]) -> float | int | None:
    """Return the primary numeric metric from the first result row."""
    if not rows:
        return None

    row = rows[0]
    for key in ("actual", "actual_count", "retention_pct", "sync_pct", "drift_pct", "value"):
        candidate = row.get(key)
        if isinstance(candidate, (int, float)):
            return candidate

    for value in row.values():
        if isinstance(value, (int, float)):
            return value
    return None


def evaluate_expectation(
    expect: CheckExpectation,
    actual: float | int | None,
) -> CheckStatus:
    """Compare an actual metric value against a check expectation."""
    if actual is None:
        return "fail"

    if expect.kind in {"min_count", "min_retention_pct", "min_sync_pct"}:
        return "pass" if float(actual) >= expect.value else "fail"

    if expect.kind == "max_drift_pct":
        if float(actual) <= expect.value:
            return "pass"
        tolerance = expect.tolerance if expect.tolerance is not None else 0.0
        if float(actual) <= expect.value + tolerance:
            return "warn"
        return "fail"

    if expect.kind == "source_parity":
        return "pass" if float(actual) == expect.value else "fail"

    return "fail"


def result_from_rows(check: CompiledCheck, rows: list[dict[str, Any]]) -> CheckResult:
    """Build a check result from SQL output rows."""
    actual = extract_metric(rows)
    status = evaluate_expectation(check.expect, actual)
    evidence = {"rows": rows, "evidence_key": check.evidence_key}
    return CheckResult(
        check_id=check.check_id,
        status=status,
        actual=actual,
        expected=check.expect.value,
        evidence=evidence,
    )
