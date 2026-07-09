"""Snowflake warehouse executor for production audits."""

from __future__ import annotations

import os
from typing import Any

from trustline.config import Profile
from trustline.exceptions import ExecutorError
from trustline.executors.base import CheckResult, CompiledCheck, result_from_rows

_REQUIRED_ENV_VARS = (
    "SNOWFLAKE_ACCOUNT",
    "SNOWFLAKE_USER",
    "SNOWFLAKE_PASSWORD",
    "SNOWFLAKE_WAREHOUSE",
)


def _import_connector() -> Any:
    """Import Snowflake connector or raise a clear install error."""
    try:
        import snowflake.connector  # type: ignore[import-not-found]
    except ImportError as exc:
        msg = (
            "snowflake-connector-python is not installed; "
            "install with `pip install trustline[snowflake]`"
        )
        raise ExecutorError(msg) from exc
    return snowflake.connector


def _resolve_database_and_schema(profile: Profile | None) -> tuple[str | None, str | None]:
    """Resolve database and schema from profile or environment."""
    if profile is not None:
        return profile.database, profile.schema
    return os.environ.get("SNOWFLAKE_DATABASE"), os.environ.get("SNOWFLAKE_SCHEMA")


class SnowflakeExecutor:
    """Execute Trustline checks against Snowflake."""

    def __init__(self, connection: Any) -> None:
        self._connection = connection

    @classmethod
    def from_env(cls, profile: Profile | None = None) -> SnowflakeExecutor:
        """Create an executor from ``SNOWFLAKE_*`` environment variables."""
        connector = _import_connector()
        missing = [name for name in _REQUIRED_ENV_VARS if not os.environ.get(name)]
        database, schema = _resolve_database_and_schema(profile)
        if profile is None:
            if not database:
                missing.append("SNOWFLAKE_DATABASE")
            if not schema:
                missing.append("SNOWFLAKE_SCHEMA")
        if missing:
            msg = f"missing Snowflake environment variables: {', '.join(missing)}"
            raise ExecutorError(msg)

        connect_kwargs: dict[str, str] = {
            "account": os.environ["SNOWFLAKE_ACCOUNT"],
            "user": os.environ["SNOWFLAKE_USER"],
            "password": os.environ["SNOWFLAKE_PASSWORD"],
            "warehouse": os.environ["SNOWFLAKE_WAREHOUSE"],
        }
        if database:
            connect_kwargs["database"] = database
        if schema:
            connect_kwargs["schema"] = schema
        role = os.environ.get("SNOWFLAKE_ROLE")
        if role:
            connect_kwargs["role"] = role

        try:
            connection = connector.connect(**connect_kwargs)
        except connector.errors.Error as exc:
            msg = f"failed to connect to Snowflake: {exc}"
            raise ExecutorError(msg) from exc
        return cls(connection)

    def execute(self, sql: str) -> list[dict[str, Any]]:
        """Execute SQL and return rows as dictionaries."""
        connector = _import_connector()
        cursor = self._connection.cursor(connector.DictCursor)
        try:
            cursor.execute(sql)
            rows = cursor.fetchall()
            return [{str(key).lower(): value for key, value in row.items()} for row in rows]
        except connector.errors.Error as exc:
            msg = f"Snowflake query failed: {exc}"
            raise ExecutorError(msg) from exc
        finally:
            cursor.close()

    def execute_check(self, check: CompiledCheck) -> CheckResult:
        """Execute a compiled check and evaluate its result."""
        rows = self.execute(check.sql)
        return result_from_rows(check, rows)

    def close(self) -> None:
        """Close the underlying Snowflake connection."""
        self._connection.close()

    def __enter__(self) -> SnowflakeExecutor:
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()
