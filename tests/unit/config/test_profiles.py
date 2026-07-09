"""Tests for profile config loading."""

from pathlib import Path

import pytest

from trustline.config import Profile, load_profile, load_profiles, resolve_duckdb_path
from trustline.exceptions import TrustlineError, ValidationError

FIXTURES_DIR = Path(__file__).resolve().parents[2] / "fixtures" / "profiles"
EXAMPLE_PROFILES = (
    Path(__file__).resolve().parents[3] / "examples" / "acme_stream" / "profiles.yml.example"
)


def test_load_profile_default_from_example() -> None:
    """Example profiles file should load the default DuckDB profile."""
    profile = load_profile("default", EXAMPLE_PROFILES)
    assert profile == Profile(
        name="default",
        target="duckdb",
        database="main",
        schema="main",
        duckdb_path="demo.duckdb",
    )


def test_resolve_duckdb_path_relative_to_profiles_file() -> None:
    """DuckDB paths should resolve relative to the profiles file directory."""
    profile = load_profile("default", EXAMPLE_PROFILES)
    resolved = resolve_duckdb_path(profile, EXAMPLE_PROFILES)
    assert resolved.name == "demo.duckdb"
    assert resolved.parent == EXAMPLE_PROFILES.parent


def test_resolve_duckdb_path_falls_back_to_acme_demo_from_repo_root(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Root profiles.yml with demo.duckdb should find the bundled ACME database."""
    repo_root = Path(__file__).resolve().parents[3]
    root_profiles = tmp_path / "profiles.yml"
    root_profiles.write_text(
        "default:\n  target: duckdb\n  database: main\n  schema: main\n"
        "  duckdb_path: demo.duckdb\n",
        encoding="utf-8",
    )
    acme_demo = tmp_path / "examples" / "acme_stream"
    acme_demo.mkdir(parents=True)
    (acme_demo / "demo.duckdb").write_bytes(
        (repo_root / "examples" / "acme_stream" / "demo.duckdb").read_bytes()
    )
    monkeypatch.chdir(tmp_path)

    profile = load_profile("default", root_profiles)
    resolved = resolve_duckdb_path(profile, root_profiles)
    assert resolved == (acme_demo / "demo.duckdb").resolve()


def test_load_profiles_returns_all_entries() -> None:
    """All profiles in a file should be returned."""
    profiles = load_profiles(FIXTURES_DIR / "valid_profiles.yml")
    assert set(profiles) == {"default", "acme_prod"}
    assert profiles["acme_prod"].target == "snowflake"


def test_load_profile_missing_name_raises() -> None:
    """Unknown profile name should raise TrustlineError."""
    with pytest.raises(TrustlineError, match="profile not found"):
        load_profile("missing", FIXTURES_DIR / "valid_profiles.yml")


def test_load_profile_missing_required_field_raises() -> None:
    """Profiles missing required keys should raise ValidationError."""
    with pytest.raises(ValidationError, match="missing required fields"):
        load_profile("default", FIXTURES_DIR / "missing_schema.yml")


def test_load_profiles_missing_file_raises() -> None:
    """Missing profiles file should raise FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        load_profiles(Path("/nonexistent/profiles.yml"))
