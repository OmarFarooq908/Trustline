"""Tests for stub CLI subcommands."""

from typer.testing import CliRunner

from trustline.cli.main import app


def test_audit_help(cli_runner: CliRunner) -> None:
    """audit --help should describe the scorecard command."""
    result = cli_runner.invoke(app, ["audit", "--help"])
    assert result.exit_code == 0
    assert "scorecard" in result.stdout.lower()
