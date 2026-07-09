"""Shared pytest fixtures."""

from collections.abc import Iterator

import pytest
from typer.testing import CliRunner

from trustline.cli.main import app


@pytest.fixture
def cli_runner() -> CliRunner:
    """Return a Typer CLI test runner."""
    return CliRunner()


@pytest.fixture
def trustline_app() -> Iterator[None]:
    """Provide the root Trustline Typer application for CLI tests."""
    yield app
