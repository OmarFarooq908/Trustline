"""Tests for profile config loading."""

from pathlib import Path

import pytest

from trustline.config import Profile, load_profile, load_profiles
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
        duckdb_path="examples/acme_stream/demo.duckdb",
    )


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
