"""Tests for JSON Schema contract validation."""

from pathlib import Path

import pytest

from trustline.contracts.models import FunnelContract
from trustline.contracts.validator import (
    validate_contract,
    validate_contract_file,
    validate_contract_strict,
    validate_contracts_dir,
)
from trustline.exceptions import ValidationError


def test_validate_contract_strict_acme_funnel(acme_contracts_dir: Path) -> None:
    """Valid ACME funnel should pass strict validation."""
    from trustline.contracts.loader import load_contract_raw

    data = load_contract_raw(acme_contracts_dir / "training_positives.yaml")
    contract = validate_contract_strict(data)
    assert isinstance(contract, FunnelContract)


def test_validate_contract_returns_field_paths(invalid_contracts_dir: Path) -> None:
    """Schema errors should include JSON paths."""
    from trustline.contracts.loader import load_contract_raw

    data = load_contract_raw(invalid_contracts_dir / "bad_retention.yaml")
    errors = validate_contract(data)
    assert errors
    assert any("expect_retention_pct" in error for error in errors)


def test_validate_contract_strict_raises(invalid_contracts_dir: Path) -> None:
    """Invalid contract should raise ValidationError."""
    from trustline.contracts.loader import load_contract_raw

    data = load_contract_raw(invalid_contracts_dir / "missing_metadata.yaml")
    with pytest.raises(ValidationError):
        validate_contract_strict(data)


def test_validate_contracts_dir_acme_passes(acme_contracts_dir: Path) -> None:
    """All ACME example contracts should validate."""
    summary = validate_contracts_dir(acme_contracts_dir)
    assert summary.total == 2
    assert summary.failed == 0
    assert summary.passed == 2


def test_validate_contracts_dir_invalid_failures(invalid_contracts_dir: Path) -> None:
    """Invalid fixtures directory should report failures."""
    summary = validate_contracts_dir(invalid_contracts_dir)
    assert summary.total == 3
    assert summary.failed == 3


def test_validate_contract_file_wrong_kind(invalid_contracts_dir: Path) -> None:
    """Unsupported kind should fail validation."""
    result = validate_contract_file(invalid_contracts_dir / "wrong_kind.yaml")
    assert not result.passed
    assert result.kind == "UnknownContract"
