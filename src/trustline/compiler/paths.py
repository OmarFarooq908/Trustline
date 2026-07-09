"""Resolve paths to Jinja2 SQL templates."""

from functools import lru_cache
from pathlib import Path


@lru_cache
def template_dir() -> Path:
    """Return the directory containing Trustline SQL templates."""
    package_root = Path(__file__).resolve().parents[1]
    bundled = package_root / "templates" / "sql"
    if bundled.is_dir():
        return bundled
    repo_root = Path(__file__).resolve().parents[3]
    return repo_root / "templates" / "sql"
