"""Tests for trustline audit CLI."""

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from typer.testing import CliRunner

from trustline.cli.main import app
from trustline.config import Profile

REPO_ROOT = Path(__file__).resolve().parents[3]
ACME_CONTRACTS = REPO_ROOT / "examples" / "acme_stream" / "contracts"
ACME_PROFILES = REPO_ROOT / "examples" / "acme_stream" / "profiles.yml.example"


def test_audit_dry_run_compiles_checks(cli_runner: CliRunner) -> None:
    """audit --dry-run should compile checks without executing SQL."""
    result = cli_runner.invoke(
        app,
        [
            "audit",
            "--contracts",
            str(ACME_CONTRACTS),
            "--target",
            "duckdb",
            "--profiles",
            str(ACME_PROFILES),
            "--dry-run",
        ],
    )
    assert result.exit_code == 0
    assert "Compiled" in result.stdout
    assert "checks" in result.stdout


def test_audit_acme_demo_exits_nonzero(cli_runner: CliRunner) -> None:
    """ACME demo audit should exit 1 when seeded failures are present."""
    result = cli_runner.invoke(
        app,
        [
            "audit",
            "--contracts",
            str(ACME_CONTRACTS),
            "--target",
            "duckdb",
            "--profiles",
            str(ACME_PROFILES),
            "--output-dir",
            "/tmp/trustline-audit-test-unused",
        ],
        catch_exceptions=False,
    )
    assert result.exit_code == 1
    assert "Verdict: FAIL" in result.stdout
    assert "Phase 1 Pipeline Truth" in result.stdout


def test_audit_writes_scorecard_reports(cli_runner: CliRunner, tmp_path: Path) -> None:
    """audit should write scorecard.md and scorecard.json to --output-dir."""
    output_dir = tmp_path / "reports"
    result = cli_runner.invoke(
        app,
        [
            "audit",
            "--contracts",
            str(ACME_CONTRACTS),
            "--target",
            "duckdb",
            "--profiles",
            str(ACME_PROFILES),
            "--output-dir",
            str(output_dir),
            "-o",
            "json",
        ],
    )
    assert result.exit_code == 1
    assert (output_dir / "scorecard.md").is_file()
    assert (output_dir / "scorecard.json").is_file()
    payload = json.loads((output_dir / "scorecard.json").read_text(encoding="utf-8"))
    assert payload["verdict"] == "fail"


def test_audit_dry_run_compiles_snowflake_checks(cli_runner: CliRunner) -> None:
    """Snowflake profile dry-run should compile checks without connecting."""
    result = cli_runner.invoke(
        app,
        [
            "audit",
            "--contracts",
            str(ACME_CONTRACTS),
            "--target",
            "snowflake",
            "--profile",
            "acme_prod",
            "--profiles",
            str(REPO_ROOT / "tests" / "fixtures" / "profiles" / "valid_profiles.yml"),
            "--dry-run",
        ],
    )
    assert result.exit_code == 0
    assert "Compiled" in result.stdout


def test_build_executor_snowflake_uses_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Snowflake executor construction should delegate to from_env."""
    from trustline.cli import audit as audit_cli

    profile = Profile(
        name="acme_prod",
        target="snowflake",
        database="ANALYTICS",
        schema="ML_STAGING",
    )
    sentinel = object()
    from_env = MagicMock(return_value=sentinel)
    monkeypatch.setattr("trustline.executors.snowflake.SnowflakeExecutor.from_env", from_env)

    executor = audit_cli._build_executor(profile, ACME_PROFILES)
    assert executor is sentinel
    from_env.assert_called_once_with(profile)


def test_audit_missing_contracts_dir_exits_2(cli_runner: CliRunner) -> None:
    """Missing contracts directory should exit with code 2."""
    result = cli_runner.invoke(
        app,
        [
            "audit",
            "--contracts",
            "/path/does/not/exist",
            "--profiles",
            str(ACME_PROFILES),
        ],
    )
    assert result.exit_code == 2
