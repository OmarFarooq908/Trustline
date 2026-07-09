"""JSON Schema validation for Trustline contracts."""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError
from referencing import Registry, Resource

from trustline.contracts.models import (
    KNOWN_KINDS,
    CohortManifest,
    ContractDocument,
    FunnelContract,
)
from trustline.contracts.schemas import schema_dir
from trustline.exceptions import ValidationError

_KIND_SCHEMA_FILES = {
    "FunnelContract": "funnel.schema.json",
    "CohortManifest": "cohort.schema.json",
}


@dataclass(frozen=True)
class FileValidationResult:
    """Validation outcome for a single contract file."""

    path: Path
    kind: str | None
    passed: bool
    errors: tuple[str, ...]


@dataclass(frozen=True)
class ValidationSummary:
    """Aggregate validation outcome for a directory of contracts."""

    total: int
    passed: int
    failed: int
    results: tuple[FileValidationResult, ...]


@lru_cache
def _build_registry(directory: Path) -> Registry:
    """Load all schema files into a referencing registry."""
    registry = Registry()
    for path in sorted(directory.glob("*.schema.json")):
        contents = json.loads(path.read_text(encoding="utf-8"))
        schema_id = contents["$id"]
        registry = registry.with_resource(schema_id, Resource.from_contents(contents))
    return registry


def _validator_for_kind(kind: str, directory: Path | None = None) -> Draft202012Validator:
    """Return a JSON Schema validator for a contract kind."""
    schema_root = directory or schema_dir()
    schema_file = _KIND_SCHEMA_FILES.get(kind)
    if schema_file is None:
        msg = f"unsupported contract kind: {kind}"
        raise ValidationError(msg)

    schema_path = schema_root / schema_file
    if not schema_path.is_file():
        msg = f"schema file not found: {schema_path}"
        raise ValidationError(msg)

    contents = json.loads(schema_path.read_text(encoding="utf-8"))
    registry = _build_registry(schema_root)
    try:
        return Draft202012Validator(
            contents,
            registry=registry,
            format_checker=FormatChecker(),
        )
    except SchemaError as exc:
        msg = f"invalid schema {schema_path.name}: {exc}"
        raise ValidationError(msg) from exc


def _format_errors(errors: list[Any]) -> list[str]:
    """Convert jsonschema errors to human-readable strings."""
    formatted: list[str] = []
    for error in errors:
        path = ".".join(str(part) for part in error.path) or "(root)"
        formatted.append(f"{path}: {error.message}")
    return formatted


def validate_contract(doc: dict[str, Any], directory: Path | None = None) -> list[str]:
    """Validate a contract dict; return a list of error messages."""
    kind = doc.get("kind")
    if not isinstance(kind, str):
        return ["kind: field required"]
    if kind not in KNOWN_KINDS:
        return [f"kind: unsupported contract kind {kind!r}"]

    validator = _validator_for_kind(kind, directory)
    return _format_errors(list(validator.iter_errors(doc)))


def parse_contract_document(doc: dict[str, Any]) -> ContractDocument:
    """Parse a contract dict into a typed Pydantic model."""
    kind = doc.get("kind")
    if kind == "FunnelContract":
        return FunnelContract.model_validate(doc)
    if kind == "CohortManifest":
        return CohortManifest.model_validate(doc)
    msg = f"unsupported contract kind: {kind!r}"
    raise ValidationError(msg)


def validate_contract_strict(
    doc: dict[str, Any], directory: Path | None = None
) -> ContractDocument:
    """Validate a contract dict and return a typed model."""
    errors = validate_contract(doc, directory)
    if errors:
        msg = "; ".join(errors)
        raise ValidationError(msg)
    try:
        return parse_contract_document(doc)
    except ValueError as exc:
        raise ValidationError(str(exc)) from exc


def validate_contract_file(path: Path, directory: Path | None = None) -> FileValidationResult:
    """Validate a single contract file on disk."""
    from trustline.contracts.loader import load_contract_raw

    try:
        doc = load_contract_raw(path)
    except FileNotFoundError:
        raise
    except ValidationError as exc:
        return FileValidationResult(
            path=path,
            kind=None,
            passed=False,
            errors=(str(exc),),
        )

    kind = doc.get("kind") if isinstance(doc.get("kind"), str) else None
    if kind not in KNOWN_KINDS:
        return FileValidationResult(
            path=path,
            kind=kind,
            passed=False,
            errors=(f"kind: unsupported contract kind {kind!r}",),
        )

    schema_errors = validate_contract(doc, directory)
    if schema_errors:
        return FileValidationResult(
            path=path,
            kind=kind,
            passed=False,
            errors=tuple(schema_errors),
        )

    try:
        parse_contract_document(doc)
    except ValidationError as exc:
        return FileValidationResult(
            path=path,
            kind=kind,
            passed=False,
            errors=(str(exc),),
        )

    return FileValidationResult(path=path, kind=kind, passed=True, errors=())


def validate_contracts_dir(
    directory: Path,
    *,
    strict: bool = False,
    schema_directory: Path | None = None,
) -> ValidationSummary:
    """Validate all contract YAML files in a directory."""
    if not directory.is_dir():
        msg = f"contracts directory not found: {directory}"
        raise FileNotFoundError(msg)

    results: list[FileValidationResult] = []
    for path in sorted(directory.iterdir()):
        if not path.is_file() or path.suffix.lower() not in {".yaml", ".yml"}:
            continue
        results.append(validate_contract_file(path, schema_directory))

    passed = sum(1 for result in results if result.passed)
    failed = len(results) - passed
    if strict and failed:
        failed = len(results)
        passed = 0

    return ValidationSummary(
        total=len(results),
        passed=passed,
        failed=failed,
        results=tuple(results),
    )
