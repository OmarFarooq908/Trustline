"""Audit profile models and loading."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator
from pydantic import BaseModel, ConfigDict, Field

from trustline.contracts.schemas import schema_dir
from trustline.exceptions import ValidationError


class MigrationSpec(BaseModel):
    """Source migration metadata for volume drift checks."""

    model_config = ConfigDict(extra="forbid")

    from_source: str
    to_source: str
    cutover_date: date


class CrmCoverageSpec(BaseModel):
    """CRM mirror coverage configuration."""

    model_config = ConfigDict(extra="forbid")

    sync_table: str
    mirror_table: str
    expect_sync_pct: float = Field(ge=0, le=100)


class SourceSwapSpec(BaseModel):
    """Source swap drift configuration."""

    model_config = ConfigDict(extra="forbid")

    table: str
    migration: MigrationSpec
    volume_threshold_pct: float = Field(default=10.0, ge=0, le=100)


class ScoreDistributionSpec(BaseModel):
    """Optional score distribution stability configuration."""

    model_config = ConfigDict(extra="forbid")

    table: str


class AuditProfile(BaseModel):
    """Demo audit profile for Phase 1 and Phase 3 checks."""

    model_config = ConfigDict(extra="forbid")

    crm_coverage: CrmCoverageSpec
    source_swap: SourceSwapSpec
    score_distribution: ScoreDistributionSpec | None = None


def _validate_audit_profile_document(document: dict[str, Any]) -> list[str]:
    """Validate an audit profile document against JSON Schema."""
    schema_path = schema_dir() / "audit_profile.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    return [
        f"{'.'.join(str(part) for part in error.path)}: {error.message}"
        for error in validator.iter_errors(document)
    ]


def load_audit_profile(path: Path) -> AuditProfile:
    """Load and validate an audit profile YAML file."""
    if not path.is_file():
        msg = f"audit profile not found: {path}"
        raise FileNotFoundError(msg)

    try:
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        msg = f"malformed YAML in {path.name}: {exc}"
        raise ValidationError(msg) from exc

    if not isinstance(document, dict):
        msg = f"audit profile root must be a mapping: {path.name}"
        raise ValidationError(msg)

    errors = _validate_audit_profile_document(document)
    if errors:
        msg = "; ".join(errors)
        raise ValidationError(msg)

    return AuditProfile.model_validate(document)
