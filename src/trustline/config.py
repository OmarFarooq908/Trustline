"""Connection profile loading for warehouse executors."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from trustline.exceptions import TrustlineError, ValidationError

_REQUIRED_FIELDS = ("target", "database", "schema")


@dataclass(frozen=True)
class Profile:
    """Warehouse connection profile from ``profiles.yml``."""

    name: str
    target: str
    database: str
    schema: str
    duckdb_path: str | None = None


def _parse_profiles_document(raw: str, path: Path) -> dict[str, Any]:
    """Parse profiles YAML into a mapping."""
    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        msg = f"malformed YAML in {path}: {exc}"
        raise ValidationError(msg) from exc
    if not isinstance(data, dict) or not data:
        msg = f"profiles file must be a non-empty mapping: {path}"
        raise ValidationError(msg)
    return data


def _profile_from_mapping(name: str, values: Any) -> Profile:
    """Build a Profile from a profile entry."""
    if not isinstance(values, dict):
        msg = f"profile {name!r} must be a mapping"
        raise ValidationError(msg)

    missing = [field for field in _REQUIRED_FIELDS if field not in values]
    if missing:
        msg = f"profile {name!r} missing required fields: {', '.join(missing)}"
        raise ValidationError(msg)

    target = values["target"]
    database = values["database"]
    schema = values["schema"]
    if not all(isinstance(value, str) and value for value in (target, database, schema)):
        msg = f"profile {name!r} target, database, and schema must be non-empty strings"
        raise ValidationError(msg)

    duckdb_path = values.get("duckdb_path")
    if duckdb_path is not None and not isinstance(duckdb_path, str):
        msg = f"profile {name!r} duckdb_path must be a string"
        raise ValidationError(msg)

    return Profile(
        name=name,
        target=target,
        database=database,
        schema=schema,
        duckdb_path=duckdb_path,
    )


def load_profiles(profiles_path: Path) -> dict[str, Profile]:
    """Load all profiles from a YAML file."""
    if not profiles_path.is_file():
        msg = f"profiles file not found: {profiles_path}"
        raise FileNotFoundError(msg)

    document = _parse_profiles_document(profiles_path.read_text(encoding="utf-8"), profiles_path)
    profiles: dict[str, Profile] = {}
    for name, values in document.items():
        if not isinstance(name, str):
            msg = "profile names must be strings"
            raise ValidationError(msg)
        profiles[name] = _profile_from_mapping(name, values)
    return profiles


def load_profile(name: str, profiles_path: Path = Path("profiles.yml")) -> Profile:
    """Load a named profile from ``profiles.yml``."""
    profiles = load_profiles(profiles_path)
    profile = profiles.get(name)
    if profile is None:
        msg = f"profile not found: {name}"
        raise TrustlineError(msg)
    return profile


def resolve_profiles_path(path: Path | None = None) -> Path:
    """Resolve the profiles file, falling back to the ACME example."""
    if path is not None:
        return path
    default = Path("profiles.yml")
    if default.is_file():
        return default
    example = Path("examples/acme_stream/profiles.yml.example")
    if example.is_file():
        return example
    return default


def resolve_duckdb_path(profile: Profile, profiles_path: Path) -> Path:
    """Resolve a profile DuckDB path relative to the profiles file."""
    if not profile.duckdb_path:
        msg = f"profile {profile.name!r} is missing duckdb_path"
        raise TrustlineError(msg)
    database = Path(profile.duckdb_path)
    if not database.is_absolute():
        database = (profiles_path.parent / database).resolve()
    return database
