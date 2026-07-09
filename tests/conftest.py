"""Shared pytest fixtures."""

from collections.abc import Iterator
from pathlib import Path

import pytest
from typer.testing import CliRunner

from trustline.cli.main import app

REPO_ROOT = Path(__file__).resolve().parents[1]
ACME_CONTRACTS_DIR = REPO_ROOT / "examples" / "acme_stream" / "contracts"
FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
INVALID_CONTRACTS_DIR = FIXTURES_DIR / "invalid_contracts"
ACME_FIXTURES_DIR = FIXTURES_DIR / "acme_contracts"


@pytest.fixture
def cli_runner() -> CliRunner:
    """Return a Typer CLI test runner."""
    return CliRunner()


@pytest.fixture
def trustline_app() -> Iterator[None]:
    """Provide the root Trustline Typer application for CLI tests."""
    yield app


@pytest.fixture
def acme_contracts_dir() -> Path:
    """Path to ACME Stream example contracts."""
    return ACME_CONTRACTS_DIR


@pytest.fixture
def invalid_contracts_dir() -> Path:
    """Path to invalid contract fixtures."""
    return INVALID_CONTRACTS_DIR
