"""Tests for package version fallback."""

from importlib.metadata import PackageNotFoundError
from unittest.mock import patch

import trustline


def test_version_fallback_when_package_not_found() -> None:
    """__version__ should fall back when distribution metadata is missing."""
    with patch("trustline.version", side_effect=PackageNotFoundError("trustline")):
        # Re-import to exercise fallback (reload module)
        import importlib

        import trustline as tl

        importlib.reload(tl)
        assert tl.__version__ == "0.1.1"

    # Restore normal version after reload side effects
    import importlib

    importlib.reload(trustline)
