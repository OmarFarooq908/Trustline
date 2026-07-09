"""Additional validator coverage tests."""

from pathlib import Path

import pytest

from trustline.contracts.schemas import schema_dir
from trustline.contracts.validator import _validator_for_kind, validate_contract
from trustline.exceptions import ValidationError


def test_validate_contract_unknown_kind() -> None:
    """Unknown kinds should return an error message."""
    errors = validate_contract({"kind": "NotARealKind"})
    assert errors == ["kind: unsupported contract kind 'NotARealKind'"]


def test_validate_contract_missing_kind() -> None:
    """Missing kind should return an error message."""
    errors = validate_contract({})
    assert errors == ["kind: field required"]


def test_validator_for_kind_unsupported() -> None:
    """Unsupported kind should raise ValidationError."""
    with pytest.raises(ValidationError, match="unsupported contract kind"):
        _validator_for_kind("FakeKind")


def test_validator_for_kind_missing_schema_file(tmp_path: Path) -> None:
    """Missing schema file should raise ValidationError."""
    empty_dir = tmp_path / "schemas"
    empty_dir.mkdir()
    with pytest.raises(ValidationError, match="schema file not found"):
        _validator_for_kind("FunnelContract", empty_dir)


def test_schema_dir_finds_repo_schemas() -> None:
    """Schema directory should resolve to bundled or repo schemas."""
    directory = schema_dir()
    assert (directory / "funnel.schema.json").is_file()
