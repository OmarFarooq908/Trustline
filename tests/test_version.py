"""Tests for package version."""

import trustline


def test_version_is_string() -> None:
    """Package version should be a non-empty semver-like string."""
    assert isinstance(trustline.__version__, str)
    assert trustline.__version__
    parts = trustline.__version__.split(".")
    assert len(parts) >= 2
