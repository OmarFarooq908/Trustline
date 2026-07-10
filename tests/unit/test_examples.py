"""Tests for bundled example fixtures."""

from __future__ import annotations

from trustline.examples import acme_stream_dir


def test_acme_stream_dir_contains_fixture_files() -> None:
    """Bundled ACME directory should include contracts, profile, and database."""
    root = acme_stream_dir()
    assert root.is_dir()
    assert (root / "contracts" / "training_positives.yaml").is_file()
    assert (root / "audit_profile.yaml").is_file()
    assert (root / "profiles.yml.example").is_file()
    assert (root / "demo.duckdb").is_file()


def test_acme_stream_dir_name() -> None:
    """Path should end at the acme_stream fixture directory."""
    root = acme_stream_dir()
    assert root.name == "acme_stream"
