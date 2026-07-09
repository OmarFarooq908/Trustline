"""Snowflake integration tests (skipped unless explicitly enabled)."""

from __future__ import annotations

import os

import pytest

from trustline.exceptions import ExecutorError
from trustline.executors.snowflake import SnowflakeExecutor

pytestmark = pytest.mark.integration


def _integration_enabled() -> None:
    if os.environ.get("TRUSTLINE_RUN_INTEGRATION") != "1":
        pytest.skip("set TRUSTLINE_RUN_INTEGRATION=1 to run integration tests")
    pytest.importorskip("snowflake.connector")
    required = (
        "SNOWFLAKE_ACCOUNT",
        "SNOWFLAKE_USER",
        "SNOWFLAKE_PASSWORD",
        "SNOWFLAKE_WAREHOUSE",
        "SNOWFLAKE_DATABASE",
        "SNOWFLAKE_SCHEMA",
    )
    missing = [name for name in required if not os.environ.get(name)]
    if missing:
        pytest.skip(f"missing Snowflake credentials: {', '.join(missing)}")


def test_snowflake_executor_runs_simple_query() -> None:
    """Live Snowflake connection should execute a trivial query."""
    _integration_enabled()
    try:
        with SnowflakeExecutor.from_env() as executor:
            rows = executor.execute("SELECT 1 AS value")
    except ExecutorError as exc:
        pytest.skip(f"Snowflake unavailable: {exc}")

    assert rows == [{"value": 1}]
