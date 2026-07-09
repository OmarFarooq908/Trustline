"""Tests for contract YAML loader."""

from pathlib import Path

import pytest

from trustline.contracts.loader import load_contract, load_contracts_dir
from trustline.contracts.models import FunnelContract
from trustline.exceptions import ValidationError


def test_load_contract_acme_funnel(acme_contracts_dir: Path) -> None:
    """Load valid ACME funnel contract."""
    contract = load_contract(acme_contracts_dir / "training_positives.yaml")
    assert isinstance(contract, FunnelContract)
    assert contract.metadata.name == "training_positives"


def test_load_contracts_dir(acme_contracts_dir: Path) -> None:
    """Load all contracts from ACME examples directory."""
    contracts = load_contracts_dir(acme_contracts_dir)
    kinds = {contract.kind for contract in contracts}
    assert kinds == {"FunnelContract", "CohortManifest"}
    assert len(contracts) == 2


def test_load_contract_missing_file() -> None:
    """Missing file should raise FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        load_contract(Path("/nonexistent/contract.yaml"))


def test_load_contract_malformed_yaml(tmp_path: Path) -> None:
    """Malformed YAML should raise ValidationError."""
    path = tmp_path / "bad.yaml"
    path.write_text("apiVersion: [\n", encoding="utf-8")
    with pytest.raises(ValidationError, match="malformed YAML"):
        load_contract(path)


def test_load_contract_invalid_schema(invalid_contracts_dir: Path) -> None:
    """Schema-invalid contract should raise ValidationError."""
    with pytest.raises(ValidationError):
        load_contract(invalid_contracts_dir / "bad_retention.yaml")
