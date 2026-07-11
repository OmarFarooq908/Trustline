"""Tests for trustline audit CLI."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

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
    assert "Overall Trust Score" in result.stdout
    assert "Pipeline Truth" in result.stdout


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


def test_audit_notify_slack_on_failure(cli_runner: CliRunner) -> None:
    """Failed audit with --notify slack should post to the webhook."""
    with patch("trustline.integrations.slack.notify_audit_failure") as notify:
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
                "--notify",
                "slack",
                "--slack-webhook",
                "https://hooks.slack.com/services/test",
                "-o",
                "json",
            ],
        )
    assert result.exit_code == 1
    notify.assert_called_once()
    assert notify.call_args.args[0] == "https://hooks.slack.com/services/test"


def test_audit_unsupported_notify_channel_exits_2(cli_runner: CliRunner) -> None:
    """Unsupported --notify channel should exit with code 2."""
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
            "--notify",
            "email",
        ],
    )
    assert result.exit_code == 2
    assert "unsupported notification channel" in result.stderr


def test_audit_demo_runs_acme_fixture(cli_runner: CliRunner, tmp_path: Path) -> None:
    """audit --demo should run bundled ACME without extra flags."""
    output_dir = tmp_path / "reports"
    result = cli_runner.invoke(
        app,
        ["audit", "--demo", "--output-dir", str(output_dir)],
        catch_exceptions=False,
    )
    assert result.exit_code == 1
    assert "Demo audit" in result.stdout
    assert "Overall Trust Score" in result.stdout
    payload = json.loads((output_dir / "scorecard.json").read_text(encoding="utf-8"))
    assert payload["verdict"] == "fail"


def test_audit_demo_shows_banner(cli_runner: CliRunner) -> None:
    """Demo banner should mention expected exit code 1."""
    result = cli_runner.invoke(app, ["audit", "--demo", "--dry-run"])
    assert result.exit_code == 0
    assert "exit code 1 is expected" in result.stdout


def test_audit_missing_contracts_dir_shows_hint(cli_runner: CliRunner) -> None:
    """Missing contracts directory should include init hint."""
    result = cli_runner.invoke(
        app,
        ["audit", "--contracts", "/path/does/not/exist", "--profiles", str(ACME_PROFILES)],
    )
    assert result.exit_code == 2
    assert "trustline init" in result.stderr
    assert "trustline audit --demo" in result.stderr


def test_audit_missing_profiles_shows_hint(cli_runner: CliRunner) -> None:
    """Missing profiles file should suggest demo or init."""
    result = cli_runner.invoke(
        app,
        ["audit", "--contracts", str(ACME_CONTRACTS), "--profiles", "/no/profiles.yml"],
    )
    assert result.exit_code == 2
    assert "trustline audit --demo" in result.stderr
