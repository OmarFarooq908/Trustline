"""Bundled contract template presets for trustline init."""

from __future__ import annotations

from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path


@dataclass(frozen=True)
class InitPreset:
    """Files copied by ``trustline init --preset``."""

    name: str
    description: str
    pattern_doc: str
    contract_files: tuple[str, ...]
    include_audit_profile: bool


PRESETS: dict[str, InitPreset] = {
    "ml-crm-boundary": InitPreset(
        name="ml-crm-boundary",
        description="ML → CRM boundary pack: funnel, cohort source parity, CRM coverage",
        pattern_doc="docs/patterns/README.md",
        contract_files=("funnel_retention.yaml", "cohort_source_parity.yaml"),
        include_audit_profile=True,
    ),
    "funnel-retention": InitPreset(
        name="funnel-retention",
        description="Identity funnel retention across join stages",
        pattern_doc="docs/patterns/identity-funnel-collapse.md",
        contract_files=("funnel_retention.yaml",),
        include_audit_profile=False,
    ),
    "cohort-source-parity": InitPreset(
        name="cohort-source-parity",
        description="Training vs scoring feature source parity",
        pattern_doc="docs/patterns/training-serving-divergence.md",
        contract_files=("cohort_source_parity.yaml",),
        include_audit_profile=False,
    ),
}


def templates_dir() -> Path:
    """Return path to bundled contract template YAML files."""
    bundled = Path(str(files("trustline").joinpath("templates", "contracts")))
    if bundled.is_dir():
        return bundled
    repo = Path(__file__).resolve().parent / "contracts"
    if repo.is_dir():
        return repo
    return bundled


def list_presets() -> list[str]:
    """Preset names available for trustline init."""
    return sorted(PRESETS.keys())
