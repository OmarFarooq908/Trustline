"""Tests for trustline validate CLI."""

from pathlib import Path

from typer.testing import CliRunner

from trustline.cli.main import app


def test_validate_acme_contracts_exit_zero(
    cli_runner: CliRunner,
    acme_contracts_dir: Path,
) -> None:
    """Valid ACME contracts directory should exit 0."""
    result = cli_runner.invoke(
        app,
        ["validate", "--contracts", str(acme_contracts_dir)],
    )
    assert result.exit_code == 0
    assert "All contracts valid." in result.stdout
    assert "training_positives.yaml" in result.stdout


def test_validate_invalid_contracts_exit_one(
    cli_runner: CliRunner,
    invalid_contracts_dir: Path,
) -> None:
    """Invalid contracts should exit 1."""
    result = cli_runner.invoke(
        app,
        ["validate", "--contracts", str(invalid_contracts_dir)],
    )
    assert result.exit_code == 1
    assert "Validation failed." in result.stdout


def test_validate_missing_directory_exit_two(cli_runner: CliRunner) -> None:
    """Missing contracts directory should exit 2."""
    result = cli_runner.invoke(
        app,
        ["validate", "--contracts", "/nonexistent/contracts"],
    )
    assert result.exit_code == 2
    assert "not found" in result.stderr.lower() or "not found" in result.stdout.lower()


def test_validate_single_file_flag(
    cli_runner: CliRunner,
    acme_contracts_dir: Path,
) -> None:
    """--file should validate a single contract."""
    path = acme_contracts_dir / "training_positives.yaml"
    result = cli_runner.invoke(app, ["validate", "--file", str(path)])
    assert result.exit_code == 0
    assert "PASS" in result.stdout


def test_validate_single_missing_file_exit_two(cli_runner: CliRunner) -> None:
    """Missing --file path should exit 2."""
    result = cli_runner.invoke(app, ["validate", "--file", "/nonexistent.yaml"])
    assert result.exit_code == 2
