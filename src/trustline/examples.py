"""Bundled example fixtures shipped with the wheel."""

from __future__ import annotations

from importlib.resources import files
from pathlib import Path


def acme_stream_dir() -> Path:
    """Return path to the bundled ACME Stream example directory."""
    bundled = Path(str(files("trustline").joinpath("examples", "acme_stream")))
    if bundled.is_dir() and (bundled / "demo.duckdb").is_file():
        return bundled

    # Editable install from repository clone (wheel bundles examples; dev uses repo path).
    repo_fixture = Path(__file__).resolve().parents[2] / "examples" / "acme_stream"
    if repo_fixture.is_dir():
        return repo_fixture

    return bundled
