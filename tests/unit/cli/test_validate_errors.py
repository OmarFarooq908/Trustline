"""Additional tests for trustline validate CLI edge cases."""

from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from trustline.cli.main import app


def test_validate_empty_directory_exit_two(cli_runner: CliRunner, tmp_path: Path) -> None:
    """Empty contracts directory should exit 2."""
    result = cli_runner.invoke(app, ["validate", "--contracts", str(tmp_path)])
    assert result.exit_code == 2
    assert "No contract files found" in result.stdout


def test_validate_internal_error_exit_three(cli_runner: CliRunner, tmp_path: Path) -> None:
    """Unexpected errors should exit 3."""
    contracts_dir = tmp_path / "contracts"
    contracts_dir.mkdir()
    (contracts_dir / "sample.yaml").write_text("kind: FunnelContract\n", encoding="utf-8")

    with patch(
        "trustline.cli.validate.validate_contracts_dir",
        side_effect=RuntimeError("boom"),
    ):
        result = cli_runner.invoke(app, ["validate", "--contracts", str(contracts_dir)])

    assert result.exit_code == 3
    assert "internal error" in result.stderr.lower() or "boom" in result.stderr.lower()
