"""Unit tests for Snowflake executor."""

from __future__ import annotations

import os
import sys
import types
from unittest.mock import MagicMock, patch

import pytest

from trustline.config import Profile
from trustline.exceptions import ExecutorError
from trustline.executors.base import CheckExpectation, CompiledCheck
from trustline.executors.snowflake import SnowflakeExecutor, _import_connector


def _mock_connector_module() -> MagicMock:
    connector = MagicMock()
    connector.errors.Error = Exception
    connector.DictCursor = object
    return connector


def test_import_connector_raises_when_package_missing() -> None:
    """Missing snowflake-connector-python should raise ExecutorError."""
    fake_snowflake = types.ModuleType("snowflake")
    with (
        patch.dict(sys.modules, {"snowflake": fake_snowflake}),
        pytest.raises(ExecutorError, match="snowflake-connector-python"),
    ):
        _import_connector()


def test_from_env_requires_credentials() -> None:
    """from_env should fail fast when required env vars are missing."""
    connector = _mock_connector_module()
    with (
        patch("trustline.executors.snowflake._import_connector", return_value=connector),
        patch.dict(os.environ, {}, clear=True),
        pytest.raises(ExecutorError, match="missing Snowflake environment variables"),
    ):
        SnowflakeExecutor.from_env()


def test_from_env_uses_profile_database_and_schema() -> None:
    """Profile database and schema should override env-only resolution."""
    connector = _mock_connector_module()
    connection = MagicMock()
    connector.connect.return_value = connection
    profile = Profile(
        name="acme_prod",
        target="snowflake",
        database="ANALYTICS",
        schema="ML_STAGING",
    )
    env = {
        "SNOWFLAKE_ACCOUNT": "acct",
        "SNOWFLAKE_USER": "user",
        "SNOWFLAKE_PASSWORD": "secret",
        "SNOWFLAKE_WAREHOUSE": "WH",
    }
    with (
        patch("trustline.executors.snowflake._import_connector", return_value=connector),
        patch.dict(os.environ, env, clear=True),
    ):
        executor = SnowflakeExecutor.from_env(profile)

    connector.connect.assert_called_once_with(
        account="acct",
        user="user",
        password="secret",
        warehouse="WH",
        database="ANALYTICS",
        schema="ML_STAGING",
    )
    assert executor._connection is connection


def test_execute_normalizes_column_names_to_lowercase() -> None:
    """Snowflake result columns should be normalized for metric extraction."""
    connector = _mock_connector_module()
    cursor = MagicMock()
    cursor.fetchall.return_value = [{"VALUE": 1}]
    connection = MagicMock()
    connection.cursor.return_value = cursor

    with patch("trustline.executors.snowflake._import_connector", return_value=connector):
        executor = SnowflakeExecutor(connection)
        rows = executor.execute("SELECT 1 AS value")

    assert rows == [{"value": 1}]
    cursor.close.assert_called_once()


def test_execute_check_evaluates_result() -> None:
    """execute_check should evaluate compiled checks like other executors."""
    connector = _mock_connector_module()
    cursor = MagicMock()
    cursor.fetchall.return_value = [{"ACTUAL_COUNT": 5}]
    connection = MagicMock()
    connection.cursor.return_value = cursor
    check = CompiledCheck(
        check_id="demo.count",
        phase=2,
        sql="SELECT 5 AS actual_count",
        expect=CheckExpectation(kind="min_count", value=3),
        evidence_key="demo",
    )

    with patch("trustline.executors.snowflake._import_connector", return_value=connector):
        executor = SnowflakeExecutor(connection)
        result = executor.execute_check(check)

    assert result.status == "pass"
    assert result.actual == 5


def test_execute_invalid_sql_raises_executor_error() -> None:
    """Snowflake SQL failures should surface as ExecutorError."""
    connector = _mock_connector_module()
    cursor = MagicMock()
    cursor.execute.side_effect = Exception("syntax error")
    connection = MagicMock()
    connection.cursor.return_value = cursor

    with (
        patch("trustline.executors.snowflake._import_connector", return_value=connector),
        pytest.raises(ExecutorError, match="Snowflake query failed"),
    ):
        SnowflakeExecutor(connection).execute("SELECT bad sql")


def test_context_manager_closes_connection() -> None:
    """Snowflake executor should close connections on context exit."""
    connection = MagicMock()
    with SnowflakeExecutor(connection):
        pass
    connection.close.assert_called_once()
