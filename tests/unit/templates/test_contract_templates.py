"""Tests for bundled contract templates."""

from __future__ import annotations

import yaml

from trustline.contracts.validator import validate_contract
from trustline.templates.presets import PRESETS, templates_dir
from trustline.templates.render import DEFAULT_INIT_VARS, render_template


def _rendered_contract(name: str) -> dict:
    raw = (templates_dir() / name).read_text(encoding="utf-8")
    rendered = render_template(raw, DEFAULT_INIT_VARS)
    data = yaml.safe_load(rendered)
    assert isinstance(data, dict)
    return data


def test_funnel_retention_template_validates() -> None:
    """Rendered funnel template should pass JSON Schema validation."""
    errors = validate_contract(_rendered_contract("funnel_retention.yaml"))
    assert errors == []


def test_cohort_source_parity_template_validates() -> None:
    """Rendered cohort template should pass JSON Schema validation."""
    errors = validate_contract(_rendered_contract("cohort_source_parity.yaml"))
    assert errors == []


def test_all_presets_reference_existing_templates() -> None:
    """Every preset contract file should exist in the templates directory."""
    root = templates_dir()
    for preset in PRESETS.values():
        for filename in preset.contract_files:
            assert (root / filename).is_file(), f"missing template {filename} for {preset.name}"
        if preset.include_audit_profile:
            assert (root / "audit_profile_ml_crm.yaml").is_file()
