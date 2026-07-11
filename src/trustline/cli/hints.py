"""Actionable next-step hints for CLI error paths."""

from __future__ import annotations

from pathlib import Path


def hint_missing_contracts_dir(path: Path) -> str:
    """Hint when the contracts directory does not exist."""
    return (
        f"ERROR: contracts directory not found: {path}\n"
        "Hint: run `trustline init --preset ml-crm-boundary` to scaffold ./trustline/, "
        "or `trustline audit --demo` to try the bundled ACME fixture."
    )


def hint_missing_profiles(path: Path) -> str:
    """Hint when profiles.yml is missing."""
    return (
        f"ERROR: profiles file not found: {path}\n"
        "Hint: copy profiles.yml from `trustline init`, or run `trustline audit --demo` "
        "which uses the bundled ACME profiles."
    )


def hint_no_contract_files() -> str:
    """Hint when the contracts directory is empty."""
    return (
        "ERROR: no contract files found.\n"
        "Hint: add FunnelContract or CohortManifest YAML under --contracts, "
        "or run `trustline init --preset funnel-retention`."
    )


def hint_missing_duckdb(database: Path, profiles_path: Path) -> str:
    """Hint when the DuckDB database file is missing."""
    return (
        f"ERROR: DuckDB database not found: {database}\n"
        "Hint: set duckdb_path in your profiles file (relative to the profiles file), "
        f"e.g. duckdb_path: {database.name} next to {profiles_path.name}."
    )


def hint_missing_duckdb_path(profile_name: str) -> str:
    """Hint when a DuckDB profile omits duckdb_path."""
    return (
        f"ERROR: profile {profile_name!r} is missing duckdb_path\n"
        "Hint: add duckdb_path to the profile, e.g. duckdb_path: ./my.db"
    )


def hint_profile_not_found(name: str) -> str:
    """Hint when a named profile is missing from profiles.yml."""
    return (
        f"ERROR: profile not found: {name}\n"
        "Hint: list profile names in your profiles.yml, or use --profile default."
    )


DEMO_BANNER = (
    "Demo audit — exit code 1 is expected (seeded failures in bundled ACME fixture).\n"
    "See docs/patterns/ for what each check means.\n"
)
