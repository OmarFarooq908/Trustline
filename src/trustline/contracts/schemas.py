"""Resolve paths to JSON Schema files."""

from functools import lru_cache
from pathlib import Path


@lru_cache
def schema_dir() -> Path:
    """Return the directory containing Trustline JSON Schema files."""
    package_root = Path(__file__).resolve().parents[1]
    bundled = package_root / "schemas"
    if bundled.is_dir():
        return bundled
    repo_root = Path(__file__).resolve().parents[3]
    return repo_root / "schemas"
