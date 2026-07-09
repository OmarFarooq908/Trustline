"""DuckDB warehouse executor for local demo and tests."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import duckdb

from trustline.exceptions import ExecutorError
from trustline.executors.base import CheckResult, CompiledCheck, result_from_rows


class DuckDBExecutor:
    """Execute Trustline checks against a DuckDB database."""

    def __init__(self, database: str | Path = ":memory:") -> None:
        try:
            self._connection = duckdb.connect(str(database))
        except duckdb.Error as exc:
            msg = f"failed to connect to DuckDB database {database!r}: {exc}"
            raise ExecutorError(msg) from exc

    def execute(self, sql: str) -> list[dict[str, Any]]:
        """Execute SQL and return rows as dictionaries."""
        try:
            relation = self._connection.execute(sql)
            description = relation.description
            if description is None:
                return []
            columns = [column[0] for column in description]
            return [dict(zip(columns, row, strict=True)) for row in relation.fetchall()]
        except duckdb.Error as exc:
            msg = f"DuckDB query failed: {exc}"
            raise ExecutorError(msg) from exc

    def execute_check(self, check: CompiledCheck) -> CheckResult:
        """Execute a compiled check and evaluate its result."""
        rows = self.execute(check.sql)
        return result_from_rows(check, rows)

    def close(self) -> None:
        """Close the underlying DuckDB connection."""
        self._connection.close()

    def __enter__(self) -> DuckDBExecutor:
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()
