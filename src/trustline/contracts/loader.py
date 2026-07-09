"""Load contract YAML files into typed models."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from trustline.contracts.models import KNOWN_KINDS, ContractDocument
from trustline.contracts.validator import parse_contract_document, validate_contract_strict
from trustline.exceptions import ValidationError

_YAML_SUFFIXES = (".yaml", ".yml")


def _normalize_yaml_keys(value: Any) -> Any:
    """Restore YAML 1.1 boolean keys (e.g. ``on:``) to string keys."""
    if isinstance(value, dict):
        normalized: dict[Any, Any] = {}
        for key, item in value.items():
            normalized_key: Any = "on" if key is True else key
            normalized[normalized_key] = _normalize_yaml_keys(item)
        return normalized
    if isinstance(value, list):
        return [_normalize_yaml_keys(item) for item in value]
    return value


def _read_yaml(path: Path) -> dict[str, Any]:
    """Read and parse a YAML file."""
    if not path.is_file():
        msg = f"contract file not found: {path}"
        raise FileNotFoundError(msg)
    try:
        raw = path.read_text(encoding="utf-8")
        data = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        msg = f"malformed YAML in {path.name}: {exc}"
        raise ValidationError(msg) from exc
    if not isinstance(data, dict):
        msg = f"contract root must be a mapping: {path.name}"
        raise ValidationError(msg)
    normalized = _normalize_yaml_keys(data)
    if not isinstance(normalized, dict):
        msg = f"contract root must be a mapping: {path.name}"
        raise ValidationError(msg)
    return normalized


def load_contract(path: Path) -> ContractDocument:
    """Load and validate a single contract YAML file."""
    data = _read_yaml(path)
    return validate_contract_strict(data)


def load_contracts_dir(directory: Path) -> list[ContractDocument]:
    """Load and validate all contract YAML files in a directory."""
    if not directory.is_dir():
        msg = f"contracts directory not found: {directory}"
        raise FileNotFoundError(msg)

    documents: list[ContractDocument] = []
    paths = sorted(
        path
        for path in directory.iterdir()
        if path.is_file() and path.suffix.lower() in _YAML_SUFFIXES
    )
    for path in paths:
        kind = _peek_kind(path)
        if kind not in KNOWN_KINDS:
            continue
        documents.append(load_contract(path))
    return documents


def _peek_kind(path: Path) -> str | None:
    """Return contract kind without full validation."""
    data = _read_yaml(path)
    kind = data.get("kind")
    return kind if isinstance(kind, str) else None


def load_contract_raw(path: Path) -> dict[str, Any]:
    """Load contract YAML as a dict without schema validation."""
    return _read_yaml(path)


def document_from_dict(data: dict[str, Any]) -> ContractDocument:
    """Parse a validated contract dict into a typed model."""
    return parse_contract_document(data)
