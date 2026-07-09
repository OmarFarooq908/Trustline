"""Additional loader coverage tests."""

from pathlib import Path

import pytest

from trustline.contracts.loader import _normalize_yaml_keys, load_contracts_dir
from trustline.exceptions import ValidationError


def test_load_contracts_dir_missing() -> None:
    """Missing directory should raise FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        load_contracts_dir(Path("/nonexistent/contracts"))


def test_load_contract_non_mapping_root(tmp_path: Path) -> None:
    """YAML root must be a mapping."""
    from trustline.contracts.loader import load_contract

    path = tmp_path / "list.yaml"
    path.write_text("- item\n", encoding="utf-8")
    with pytest.raises(ValidationError, match="mapping"):
        load_contract(path)


def test_normalize_yaml_keys_nested() -> None:
    """Normalization should recurse through lists and dicts."""
    value = _normalize_yaml_keys({True: "retention_drop", "nested": [{True: "email"}]})
    assert value == {"on": "retention_drop", "nested": [{"on": "email"}]}
