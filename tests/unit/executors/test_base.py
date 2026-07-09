"""Tests for executor base types and evaluation helpers."""

from typing import Literal

import pytest

from trustline.executors.base import (
    CheckExpectation,
    CompiledCheck,
    evaluate_expectation,
    extract_metric,
    result_from_rows,
)


def test_extract_metric_prefers_named_columns() -> None:
    """Named metric columns should be preferred over arbitrary values."""
    assert extract_metric([{"retention_pct": 42.5, "other": 1}]) == 42.5


def test_extract_metric_returns_none_for_empty_rows() -> None:
    """Empty result sets should yield no metric."""
    assert extract_metric([]) is None


@pytest.mark.parametrize(
    ("kind", "actual", "expected", "status"),
    [
        ("min_count", 10, 5, "pass"),
        ("min_count", 4, 5, "fail"),
        ("min_retention_pct", 40.0, 40.0, "pass"),
        ("max_drift_pct", 8.0, 10.0, "pass"),
        ("max_drift_pct", 11.0, 10.0, "fail"),
        ("max_drift_pct", 10.5, 10.0, "warn"),
        ("source_parity", 1.0, 1.0, "pass"),
        ("source_parity", 0.0, 1.0, "fail"),
        ("positive_rate", 0.12, 0.12, "pass"),
        ("positive_rate", 0.20, 0.12, "fail"),
    ],
)
def test_evaluate_expectation(
    kind: Literal[
        "min_count",
        "min_retention_pct",
        "max_drift_pct",
        "source_parity",
        "positive_rate",
    ],
    actual: float,
    expected: float,
    status: str,
) -> None:
    """Expectation evaluation should return pass, fail, or warn."""
    tolerance = 0.02 if kind == "positive_rate" else 0.5
    expectation = CheckExpectation(kind=kind, value=expected, tolerance=tolerance)
    assert evaluate_expectation(expectation, actual) == status


def test_result_from_rows_builds_check_result() -> None:
    """Compiled checks should map SQL rows to CheckResult objects."""
    check = CompiledCheck(
        check_id="funnel.count.source_donors",
        phase=2,
        sql="SELECT 2000 AS actual_count",
        expect=CheckExpectation(kind="min_count", value=2000),
        evidence_key="source_donors",
    )
    result = result_from_rows(check, [{"actual_count": 2000}])
    assert result.status == "pass"
    assert result.actual == 2000
    assert result.expected == 2000
