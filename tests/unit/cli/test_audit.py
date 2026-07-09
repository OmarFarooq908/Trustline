"""Tests for trustline audit CLI."""

import json
from pathlib import Path

from typer.testing import CliRunner

from trustline.cli.main import app

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
