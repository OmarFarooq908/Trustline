"""Tests for DuckDB executor."""

from pathlib import Path

import pytest

from trustline.exceptions import ExecutorError
from trustline.executors.base import CheckExpectation, CompiledCheck
from trustline.executors.duckdb import DuckDBExecutor


def test_execute_select_one() -> None:
    """DuckDB executor should return rows for a simple query."""
    with DuckDBExecutor(":memory:") as executor:
        rows = executor.execute("SELECT 1 AS value")
    assert rows == [{"value": 1}]


def test_execute_check_min_count_passes() -> None:
    """execute_check should pass when the metric meets the threshold."""
    check = CompiledCheck(
        check_id="demo.count",
        phase=2,
        sql="SELECT 5 AS actual_count",
        expect=CheckExpectation(kind="min_count", value=3),
        evidence_key="demo",
    )
    with DuckDBExecutor(":memory:") as executor:
        result = executor.execute_check(check)
    assert result.status == "pass"
    assert result.actual == 5


def test_execute_check_min_count_fails() -> None:
    """execute_check should fail when the metric is below the threshold."""
    check = CompiledCheck(
        check_id="demo.count",
        phase=2,
        sql="SELECT 1 AS actual_count",
        expect=CheckExpectation(kind="min_count", value=3),
        evidence_key="demo",
    )
    with DuckDBExecutor(":memory:") as executor:
        result = executor.execute_check(check)
    assert result.status == "fail"


def test_execute_invalid_sql_raises_executor_error() -> None:
    """Invalid SQL should raise ExecutorError."""
    with DuckDBExecutor(":memory:") as executor, pytest.raises(ExecutorError, match="query failed"):
        executor.execute("SELECT FROM broken_sql")


def test_invalid_database_path_raises_executor_error(tmp_path: Path) -> None:
    """Invalid database paths should raise ExecutorError."""
    directory = tmp_path / "not_a_database"
    directory.mkdir()
    with pytest.raises(ExecutorError, match="failed to connect"):
        DuckDBExecutor(directory)
