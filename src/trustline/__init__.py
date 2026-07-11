"""Trustline — compiler for business invariants across data-product boundaries.

Public API (v0.2+):
    validate: Validate contract YAML against JSON Schema
    audit: Run five-phase trust scorecard
    init: Scaffold contracts from bundled presets (CLI only)

Current exports:
    __version__: Package version string
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("trustline")
except PackageNotFoundError:
    __version__ = "0.2.0"

__all__ = ["__version__"]
