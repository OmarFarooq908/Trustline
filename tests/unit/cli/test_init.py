"""Tests for trustline init CLI."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from trustline.cli.main import app


def test_init_ml_crm_preset_scaffolds_workspace(cli_runner: CliRunner, tmp_path: Path) -> None:
    """init should render contracts, audit profile, and profiles.yml."""
    output = tmp_path / "trustline"
    result = cli_runner.invoke(
        app,
        [
            "init",
            "--preset",
            "ml-crm-boundary",
            "--output-dir",
            str(output),
            "--non-interactive",
            "--product",
            "acme_propensity",
            "--owner",
            "ml@example.com",
        ],
    )
    assert result.exit_code == 0, result.stdout
    assert (output / "contracts" / "funnel_retention.yaml").is_file()
    assert (output / "contracts" / "cohort_source_parity.yaml").is_file()
    assert (output / "audit_profile.yaml").is_file()
    assert (output / "profiles.yml").is_file()
    assert "ml@example.com" in (output / "contracts" / "funnel_retention.yaml").read_text()


def test_init_refuses_existing_dir_without_force(cli_runner: CliRunner, tmp_path: Path) -> None:
    """init should not overwrite an existing directory without --force."""
    output = tmp_path / "trustline"
    output.mkdir()
    result = cli_runner.invoke(
        app,
        [
            "init",
            "--preset",
            "funnel-retention",
            "--output-dir",
            str(output),
            "--non-interactive",
        ],
    )
    assert result.exit_code == 2
    assert "already exists" in result.stderr


def test_init_validate_after_scaffold(cli_runner: CliRunner, tmp_path: Path) -> None:
    """Contracts from init should pass trustline validate."""
    output = tmp_path / "ws"
    init_result = cli_runner.invoke(
        app,
        [
            "init",
            "--preset",
            "funnel-retention",
            "--output-dir",
            str(output),
            "--non-interactive",
        ],
    )
    assert init_result.exit_code == 0
    validate_result = cli_runner.invoke(
        app,
        ["validate", "--contracts", str(output / "contracts")],
    )
    assert validate_result.exit_code == 0
    assert "All contracts valid" in validate_result.stdout


def test_init_unknown_preset_exits_2(cli_runner: CliRunner, tmp_path: Path) -> None:
    """init should reject unknown preset names."""
    result = cli_runner.invoke(
        app,
        [
            "init",
            "--preset",
            "does-not-exist",
            "--output-dir",
            str(tmp_path / "ws"),
            "--non-interactive",
        ],
    )
    assert result.exit_code == 2
    assert "unknown preset" in result.stderr


def test_init_force_overwrites_existing_workspace(cli_runner: CliRunner, tmp_path: Path) -> None:
    """init --force should rewrite preset contracts in an existing directory."""
    output = tmp_path / "trustline"
    cli_runner.invoke(
        app,
        [
            "init",
            "--preset",
            "funnel-retention",
            "--output-dir",
            str(output),
            "--non-interactive",
            "--product",
            "first_product",
            "--owner",
            "first@example.com",
        ],
    )
    contract_path = output / "contracts" / "funnel_retention.yaml"
    assert "first@example.com" in contract_path.read_text()

    result = cli_runner.invoke(
        app,
        [
            "init",
            "--preset",
            "funnel-retention",
            "--output-dir",
            str(output),
            "--non-interactive",
            "--force",
            "--product",
            "second_product",
            "--owner",
            "second@example.com",
        ],
    )
    assert result.exit_code == 0, result.stdout
    assert "second@example.com" in contract_path.read_text()


def test_init_cohort_source_parity_scaffold(cli_runner: CliRunner, tmp_path: Path) -> None:
    """cohort-source-parity preset should scaffold cohort contract only."""
    output = tmp_path / "trustline"
    result = cli_runner.invoke(
        app,
        [
            "init",
            "--preset",
            "cohort-source-parity",
            "--output-dir",
            str(output),
            "--non-interactive",
            "--product",
            "scoring_model",
            "--owner",
            "ml@example.com",
        ],
    )
    assert result.exit_code == 0, result.stdout
    assert (output / "contracts" / "cohort_source_parity.yaml").is_file()
    assert not (output / "contracts" / "funnel_retention.yaml").exists()
    assert not (output / "audit_profile.yaml").exists()
    assert (output / "profiles.yml").is_file()
    cohort_text = (output / "contracts" / "cohort_source_parity.yaml").read_text()
    assert "scoring_model" in cohort_text
    assert "ml@example.com" in cohort_text


def test_init_list_presets(cli_runner: CliRunner) -> None:
    """init --list-presets should print available presets."""
    result = cli_runner.invoke(app, ["init", "--list-presets"])
    assert result.exit_code == 0
    assert "ml-crm-boundary" in result.stdout
    assert "funnel-retention" in result.stdout
    assert "cohort-source-parity" in result.stdout
