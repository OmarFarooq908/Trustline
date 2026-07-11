"""Tests for CLI entrypoint."""

from typer.testing import CliRunner

from trustline.cli.main import app


def test_cli_help_exits_zero(cli_runner: CliRunner) -> None:
    """Root --help should succeed."""
    result = cli_runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "trustline" in result.stdout.lower()


def test_cli_version_exits_zero(cli_runner: CliRunner) -> None:
    """--version should print version and exit zero."""
    result = cli_runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert result.stdout.strip()


def test_validate_help_exits_zero(cli_runner: CliRunner) -> None:
    """validate --help should succeed."""
    result = cli_runner.invoke(app, ["validate", "--help"])
    assert result.exit_code == 0
    assert "validate" in result.stdout.lower()


def test_audit_help_exits_zero(cli_runner: CliRunner) -> None:
    """audit --help should succeed."""
    result = cli_runner.invoke(app, ["audit", "--help"])
    assert result.exit_code == 0
    assert "audit" in result.stdout.lower()


def test_init_help_exits_zero(cli_runner: CliRunner) -> None:
    """init --help should succeed."""
    result = cli_runner.invoke(app, ["init", "--help"])
    assert result.exit_code == 0
    assert "preset" in result.stdout.lower()
