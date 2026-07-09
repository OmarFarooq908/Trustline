"""Tests for scorecard aggregation helpers."""

import pytest

from trustline.scorecard._common import aggregate_check_status, aggregate_verdict


@pytest.mark.parametrize(
    ("statuses", "expected"),
    [
        (["pass", "pass"], "pass"),
        (["pass", "warn"], "warn"),
        (["warn", "warn"], "warn"),
        (["fail", "warn"], "fail"),
        (["skip", "pass"], "pass"),
        (["skip", "skip"], "pass"),
        (["skip", "warn"], "warn"),
        (["skip", "fail"], "fail"),
    ],
)
def test_aggregate_verdict(statuses: list[str], expected: str) -> None:
    """Overall verdict should prefer fail over warn over pass."""
    assert aggregate_verdict(statuses) == expected


@pytest.mark.parametrize(
    ("statuses", "expected"),
    [
        ([], "skip"),
        (["pass"], "pass"),
        (["warn"], "warn"),
        (["fail"], "fail"),
        (["pass", "warn"], "warn"),
        (["pass", "fail"], "fail"),
    ],
)
def test_aggregate_check_status(statuses: list[str], expected: str) -> None:
    """Phase status should prefer fail over warn over pass."""
    from trustline.executors.base import CheckResult

    checks = [
        CheckResult(
            check_id=f"check.{index}",
            status=status,  # type: ignore[arg-type]
            actual=1.0,
            expected=1.0,
            evidence={},
        )
        for index, status in enumerate(statuses)
    ]
    assert aggregate_check_status(checks) == expected
