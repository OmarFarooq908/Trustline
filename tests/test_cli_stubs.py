"""Tests for stub CLI subcommands."""

from typer.testing import CliRunner

from trustline.cli.main import app


def test_audit_stub_exits_nonzero(cli_runner: CliRunner) -> None:
    """audit without --help should report not implemented."""
    result = cli_runner.invoke(
        app,
        ["audit", "--contracts", "./examples", "--target", "duckdb"],
    )
    assert result.exit_code == 1
    assert "not yet implemented" in result.stdout.lower()
